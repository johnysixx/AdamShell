"""Independent SQLite-backed signer for symbolic replay witness revisions.

Deploy this on a separate authority host and rollback domain. SQLite WAL,
synchronous=FULL, BEGIN IMMEDIATE and monotonic CAS provide local durability
and serialization, subject to filesystem and hardware guarantees.

Never put a signer private key into the repository or checkpoint directory.
"""
import sqlite3
from contextlib import closing
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from universe.symbolic_replay_receipt_witness import (
    SymbolicReplayReceiptWitness,
)
from universe.symbolic_replay_authenticated_witness import (
    SignedSymbolicReplayWitnessRevision,
    witness_key_id,
    witness_signature_payload,
)
from universe.symbolic_replay_witness_authority import (
    SymbolicReplayWitnessAuthority,
    SymbolicReplayWitnessRevision,
)
from universe.symbolic_replay_witness_wire import (
    dumps_canonical,
    loads_strict,
)


class SQLiteWitnessAuthority:
    """Transactional durable authority. No automatic scope provisioning."""

    def __init__(self, *, database_path, signing_key):
        if not isinstance(signing_key, Ed25519PrivateKey):
            raise TypeError("Witness signing key must be Ed25519.")
        self.path = Path(database_path).resolve()
        self.signing_key = signing_key
        self.key_id = witness_key_id(
            signing_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        )
        if not self.path.is_file():
            raise FileNotFoundError(
                "Witness authority database must be explicitly provisioned."
            )

    @staticmethod
    def provision(*, database_path, universe_id, batch_sha256):
        """Operator-only command, never exposed over HTTP."""
        initial = SymbolicReplayReceiptWitness(
            universe_id=universe_id,
            batch_sha256=batch_sha256,
            receipt_ids=(),
        )
        path = Path(database_path).resolve()
        if not path.parent.is_dir():
            raise FileNotFoundError("Witness database directory missing.")

        with closing(sqlite3.connect(
            str(path), isolation_level=None, timeout=15,
        )) as connection:
            connection.execute("PRAGMA busy_timeout=15000")
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS witness_revisions (
                    universe_id TEXT NOT NULL,
                    batch_sha256 TEXT NOT NULL,
                    revision INTEGER NOT NULL CHECK (revision >= 0),
                    receipt_ids BLOB NOT NULL,
                    PRIMARY KEY (universe_id, batch_sha256)
                )"""
            )
            connection.execute("BEGIN IMMEDIATE")
            try:
                connection.execute(
                    """INSERT INTO witness_revisions
                    (universe_id, batch_sha256, revision, receipt_ids)
                    VALUES (?, ?, 0, ?)""",
                    (initial.universe_id, initial.batch_sha256,
                     dumps_canonical([])),
                )
                connection.execute("COMMIT")
            except BaseException:
                connection.execute("ROLLBACK")
                raise

    def _connect(self):
        if not self.path.is_file():
            raise FileNotFoundError("Witness database missing.")
        connection = sqlite3.connect(
            str(self.path), isolation_level=None, timeout=15,
        )
        connection.execute("PRAGMA busy_timeout=15000")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    @staticmethod
    def _decode(row, *, universe_id, batch_sha256):
        if row is None:
            raise KeyError("Witness scope not provisioned.")
        revision_number, receipt_data = row
        receipt_ids = loads_strict(receipt_data)
        if type(receipt_ids) is not list:
            raise ValueError("Corrupt witness receipt ledger.")
        return SymbolicReplayWitnessRevision(
            revision=revision_number,
            witness=SymbolicReplayReceiptWitness(
                universe_id=universe_id,
                batch_sha256=batch_sha256,
                receipt_ids=tuple(receipt_ids),
            ),
        )

    def _sign(self, revision):
        return SignedSymbolicReplayWitnessRevision(
            revision=revision,
            key_id=self.key_id,
            signature=self.signing_key.sign(
                witness_signature_payload(revision, self.key_id)
            ),
        )

    def read_current(self, *, universe_id, batch_sha256):
        # Scope inputs are canonicalized and validated by the witness.
        SymbolicReplayReceiptWitness(
            universe_id=universe_id,
            batch_sha256=batch_sha256,
            receipt_ids=(),
        )
        with closing(self._connect()) as connection:
            connection.execute("BEGIN")
            try:
                row = connection.execute(
                    """SELECT revision, receipt_ids FROM witness_revisions
                    WHERE universe_id = ? AND batch_sha256 = ?""",
                    (universe_id, batch_sha256),
                ).fetchone()
                revision = self._decode(
                    row,
                    universe_id=universe_id,
                    batch_sha256=batch_sha256,
                )
                connection.execute("COMMIT")
            except BaseException:
                connection.execute("ROLLBACK")
                raise
        return self._sign(revision)

    def publish(self, witness, *, expected_revision):
        if type(witness) is not SymbolicReplayReceiptWitness:
            raise TypeError("Proposed witness must be canonical.")
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError("Invalid expected authority revision.")

        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = connection.execute(
                    """SELECT revision, receipt_ids FROM witness_revisions
                    WHERE universe_id = ? AND batch_sha256 = ?""",
                    (witness.universe_id, witness.batch_sha256),
                ).fetchone()
                current = self._decode(
                    row,
                    universe_id=witness.universe_id,
                    batch_sha256=witness.batch_sha256,
                )
                updated = SymbolicReplayWitnessAuthority.transition(
                    current,
                    witness,
                    expected_revision=expected_revision,
                )
                if updated is not current:
                    result = connection.execute(
                        """UPDATE witness_revisions
                        SET revision = ?, receipt_ids = ?
                        WHERE universe_id = ? AND batch_sha256 = ?
                          AND revision = ?""",
                        (
                            updated.revision,
                            dumps_canonical(list(updated.witness.receipt_ids)),
                            witness.universe_id,
                            witness.batch_sha256,
                            current.revision,
                        ),
                    )
                    if result.rowcount != 1:
                        raise RuntimeError("Witness authority CAS lost.")
                # Commit before issuing a signed acknowledgement.
                connection.execute("COMMIT")
            except BaseException:
                connection.execute("ROLLBACK")
                raise
        return self._sign(updated)
