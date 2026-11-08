"""End-to-end tests for the independently deployable witness authority.

All keys/certificates are ephemeral test fixtures in a temporary directory.
The server uses real TLS sockets and the ledger uses real SQLite transactions.
"""
import io
import sqlite3
import ssl
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from cryptography.x509.oid import NameOID

from universe.universe import Universe
from universe.symbolic_replay_authenticated_witness import (
    AuthenticatedSymbolicReplayWitnessAuthority,
)
from universe.symbolic_replay_bootstrap import (
    SymbolicReplayBootstrap,
)
from universe.symbolic_replay_outbox import (
    SymbolicReplayOutboxEvent,
)
from universe.symbolic_replay_outbox_store import (
    SymbolicReplayOutboxStore,
)
from universe.symbolic_replay_witness_delivery import (
    SymbolicReplayWitnessDelivery,
)
from universe.symbolic_replay_witness_https import (
    HttpsSignedWitnessSource,
    make_https_witness_server,
)
from universe.symbolic_replay_witness_sqlite_authority import (
    SQLiteWitnessAuthority,
)
from universe.symbolic_replay_witness_wire import (
    dumps_canonical,
    loads_strict,
    signed_from_wire,
    signed_to_wire,
    witness_from_wire,
    witness_to_wire,
)


class RealWitnessAuthorityIntegrationTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory(
            prefix="a34_remote_authority_"
        )
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.db = self.base / "remote" / "authority.sqlite"
        self.db.parent.mkdir()
        self.local = self.base / "checkpoint"
        self.local.mkdir()
        self.signer = Ed25519PrivateKey.generate()
        self.public = self.signer.public_key().public_bytes(
            serialization.Encoding.Raw,
            serialization.PublicFormat.Raw,
        )
        self.token = "test-only-secret-" + "x" * 48

        # Test-only TLS CA and localhost server certificate.
        tls_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048,
        )
        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        now = datetime.now(timezone.utc)
        cert = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(tls_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=1))
            .not_valid_after(now + timedelta(days=1))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                ]),
                critical=False,
            )
            .sign(tls_key, hashes.SHA256())
        )
        self.cert = self.base / "tls-cert.pem"
        self.tls_key = self.base / "tls-key.pem"
        self.cert.write_bytes(cert.public_bytes(
            serialization.Encoding.PEM
        ))
        self.tls_key.write_bytes(tls_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ))
        self.client_context = ssl.create_default_context(
            cafile=str(self.cert)
        )

    @staticmethod
    def universe(identity):
        with redirect_stdout(io.StringIO()):
            return Universe(universe_id=identity)

    def setup_batch(self, label="normal", count=1):
        sender = self.universe("a34_" + label)
        events = tuple(
            SymbolicReplayOutboxEvent(
                id=f"a34_{label}_event_{i}",
                word_id=f"a34_{label}_word_{i}",
                sequence=i,
                message=f"A34 signed event {i}.",
            )
            for i in range(count)
        )
        sender.symbolic_replay_outbox.extend(events)
        paths = (
            self.local / "outbox.json",
            self.local / "inbox.json",
            self.local / "manifest.json",
        )
        _, receiver = SymbolicReplayBootstrap.initialize(
            sender,
            outbox_path=paths[0],
            inbox_path=paths[1],
            manifest_path=paths[2],
        )
        digest = SymbolicReplayOutboxStore.lineage_digest(
            sender.id, events
        )
        SQLiteWitnessAuthority.provision(
            database_path=self.db,
            universe_id=str(sender.id),
            batch_sha256=digest,
        )
        ledger = SQLiteWitnessAuthority(
            database_path=self.db, signing_key=self.signer,
        )
        return sender, events, paths, receiver, digest, ledger

    def start_server(self, ledger):
        server = make_https_witness_server(
            host="127.0.0.1",
            port=0,
            ledger=ledger,
            write_token=self.token,
            certfile=str(self.cert),
            keyfile=str(self.tls_key),
        )
        worker = threading.Thread(
            target=server.serve_forever,
            kwargs={"poll_interval": 0.01},
            daemon=True,
        )
        worker.start()

        def stop():
            server.shutdown()
            server.server_close()
            worker.join(timeout=3)

        self.addCleanup(stop)
        self.server = server
        return "https://localhost:" + str(
            server.server_address[1]
        )

    def make_source(self, url, *, token=None, context=None):
        return HttpsSignedWitnessSource(
            url,
            token=token,
            ssl_context=(
                self.client_context
                if context is None else context
            ),
        )

    def authority(self, source, signed_floor):
        return AuthenticatedSymbolicReplayWitnessAuthority(
            source,
            public_key_bytes=self.public,
            trusted_signed_floor=signed_floor,
        )

    def test_real_network_delivery_survives_restart(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch()
        )
        floor = ledger.read_current(
            universe_id=str(sender.id),
            batch_sha256=digest,
        )
        url = self.start_server(ledger)
        source = self.make_source(url, token=self.token)
        authority = self.authority(source, floor)
        runner = SymbolicReplayWitnessDelivery(
            sender,
            outbox_path=paths[0],
            receiver=receiver,
            witness_authority=authority,
        )
        self.assertEqual(runner.dispatch(), 1)
        self.assertTrue(
            SymbolicReplayOutboxStore.read(
                sender, paths[0]
            )[0].delivered
        )

        # Reopen actual database through a fresh authority instance.
        reopened = SQLiteWitnessAuthority(
            database_path=self.db, signing_key=self.signer,
        )
        current = reopened.read_current(
            universe_id=str(sender.id),
            batch_sha256=digest,
        )
        self.assertEqual(current.revision.revision, 1)
        self.assertEqual(
            current.revision.witness.receipt_ids,
            (events[0].id,),
        )

        recovered = self.universe(sender.id)
        report, restored_receiver = SymbolicReplayBootstrap.recover(
            recovered,
            outbox_path=paths[0],
            inbox_path=paths[1],
            manifest_path=paths[2],
            witness_authority=authority,
        )
        self.assertEqual(report.delivered_count, 1)
        self.assertEqual(len(restored_receiver.receipts), 1)

    def test_rollback_of_all_local_checkpoints_rejected(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("rollback")
        )
        original = tuple(path.read_bytes() for path in paths)
        floor = ledger.read_current(
            universe_id=str(sender.id),
            batch_sha256=digest,
        )
        url = self.start_server(ledger)
        authority = self.authority(
            self.make_source(url, token=self.token), floor,
        )
        self.assertEqual(
            SymbolicReplayWitnessDelivery(
                sender,
                outbox_path=paths[0],
                receiver=receiver,
                witness_authority=authority,
            ).dispatch(),
            1,
        )
        for path, data in zip(paths, original):
            path.write_bytes(data)

        target = self.universe(sender.id)
        with self.assertRaisesRegex(
            ValueError, "Trusted witness missing confirmed receipt"
        ):
            SymbolicReplayBootstrap.recover(
                target,
                outbox_path=paths[0],
                inbox_path=paths[1],
                manifest_path=paths[2],
                witness_authority=authority,
            )
        self.assertEqual(target.symbolic_replay_outbox, [])

    def test_concurrent_remote_compare_and_swap(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("concurrent")
        )
        url = self.start_server(ledger)
        source = self.make_source(url, token=self.token)
        floor = ledger.read_current(
            universe_id=str(sender.id), batch_sha256=digest,
        )
        authority = self.authority(source, floor)
        witness = type(floor.revision.witness)(
            universe_id=str(sender.id),
            batch_sha256=digest,
            receipt_ids=(events[0].id,),
        )
        barrier = threading.Barrier(3)
        outcomes = []
        lock = threading.Lock()

        def submit():
            barrier.wait(timeout=10)
            try:
                result = authority.publish(
                    witness, expected_revision=0,
                )
                value = ("success", result.revision)
            except Exception as error:
                value = (type(error).__name__, str(error))
            with lock:
                outcomes.append(value)

        workers = [
            threading.Thread(target=submit)
            for _ in range(2)
        ]
        for worker in workers:
            worker.start()
        barrier.wait(timeout=10)
        for worker in workers:
            worker.join(timeout=10)

        self.assertTrue(all(not w.is_alive() for w in workers))
        self.assertEqual(
            len([x for x in outcomes if x[0] == "success"]), 1,
            outcomes,
        )
        self.assertEqual(
            len([x for x in outcomes if x[0] == "RuntimeError"]), 1,
            outcomes,
        )
        self.assertEqual(
            ledger.read_current(
                universe_id=str(sender.id),
                batch_sha256=digest,
            ).revision.revision,
            1,
        )

    def test_missing_or_wrong_write_token_fails_closed(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("unauthorized")
        )
        url = self.start_server(ledger)
        floor = ledger.read_current(
            universe_id=str(sender.id), batch_sha256=digest,
        )
        witness = type(floor.revision.witness)(
            universe_id=str(sender.id),
            batch_sha256=digest,
            receipt_ids=(events[0].id,),
        )
        for token in (None, "invalid-writer-token"):
            source = self.make_source(url, token=token)
            authority = self.authority(source, floor)
            with self.assertRaises(PermissionError):
                authority.publish(witness, expected_revision=0)
        self.assertEqual(
            ledger.read_current(
                universe_id=str(sender.id),
                batch_sha256=digest,
            ).revision.revision,
            0,
        )

    def test_untrusted_tls_ca_rejected(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("tls")
        )
        url = self.start_server(ledger)
        floor = ledger.read_current(
            universe_id=str(sender.id), batch_sha256=digest,
        )
        source = HttpsSignedWitnessSource(
            url, token=self.token,
        )
        authority = self.authority(source, floor)
        with self.assertRaisesRegex(
            ConnectionError, "transport unavailable"
        ):
            authority.read_current(
                universe_id=str(sender.id),
                batch_sha256=digest,
            )

    def test_plain_http_and_tls_bypass_rejected(self):
        with self.assertRaisesRegex(
            ValueError, "HTTPS URL"
        ):
            HttpsSignedWitnessSource("http://localhost:8080")
        insecure = ssl._create_unverified_context()
        with self.assertRaisesRegex(
            ValueError, "TLS certificate verification is required"
        ):
            HttpsSignedWitnessSource(
                "https://localhost:8080",
                ssl_context=insecure,
            )

    def test_unknown_scope_is_not_auto_provisioned(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("scope")
        )
        url = self.start_server(ledger)
        source = self.make_source(url, token=self.token)
        with self.assertRaisesRegex(
            KeyError, "not provisioned"
        ):
            source.read_current(
                universe_id="unregistered",
                batch_sha256=digest,
            )

    def test_signed_floor_catches_authority_storage_rollback(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("remote_rollback")
        )
        url = self.start_server(ledger)
        source = self.make_source(url, token=self.token)
        floor0 = ledger.read_current(
            universe_id=str(sender.id), batch_sha256=digest,
        )
        authority = self.authority(source, floor0)
        witness = type(floor0.revision.witness)(
            universe_id=str(sender.id),
            batch_sha256=digest,
            receipt_ids=(events[0].id,),
        )
        self.assertEqual(
            authority.publish(witness, expected_revision=0).revision,
            1,
        )
        floor1 = ledger.read_current(
            universe_id=str(sender.id), batch_sha256=digest,
        )
        with sqlite3.connect(self.db) as connection:
            connection.execute(
                """UPDATE witness_revisions
                SET revision = 0, receipt_ids = ?
                WHERE universe_id = ? AND batch_sha256 = ?""",
                (dumps_canonical([]), str(sender.id), digest),
            )
        protected = self.authority(source, floor1)
        with self.assertRaisesRegex(
            ValueError, "below trusted floor"
        ):
            protected.read_current(
                universe_id=str(sender.id), batch_sha256=digest,
            )

    def test_duplicate_receipt_publication_idempotent(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("idempotent")
        )
        url = self.start_server(ledger)
        floor = ledger.read_current(
            universe_id=str(sender.id), batch_sha256=digest,
        )
        authority = self.authority(
            self.make_source(url, token=self.token), floor,
        )
        witness = type(floor.revision.witness)(
            universe_id=str(sender.id),
            batch_sha256=digest,
            receipt_ids=(events[0].id,),
        )
        self.assertEqual(
            authority.publish(witness, expected_revision=0).revision,
            1,
        )
        self.assertEqual(
            authority.publish(witness, expected_revision=1).revision,
            1,
        )

    def test_wire_rejects_unexpected_and_duplicate_fields(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("wire")
        )
        current = ledger.read_current(
            universe_id=str(sender.id), batch_sha256=digest,
        )
        payload = signed_to_wire(current)
        self.assertEqual(
            signed_from_wire(payload), current,
        )
        payload["unexpected"] = 1
        with self.assertRaisesRegex(
            ValueError, "Invalid signed witness fields"
        ):
            signed_from_wire(payload)
        with self.assertRaisesRegex(
            ValueError, "Duplicate JSON field"
        ):
            loads_strict(
                b'{"universe_id":"one","universe_id":"two"}'
            )

    def test_no_implicit_database_creation(self):
        missing = self.base / "remote" / "missing.sqlite"
        with self.assertRaises(FileNotFoundError):
            SQLiteWitnessAuthority(
                database_path=missing, signing_key=self.signer,
            )
        self.assertFalse(missing.exists())

    def test_scope_cannot_be_provisioned_twice(self):
        sender, events, paths, receiver, digest, ledger = (
            self.setup_batch("duplicate_scope")
        )
        with self.assertRaises(sqlite3.IntegrityError):
            SQLiteWitnessAuthority.provision(
                database_path=self.db,
                universe_id=str(sender.id),
                batch_sha256=digest,
            )


if __name__ == "__main__":
    unittest.main()
