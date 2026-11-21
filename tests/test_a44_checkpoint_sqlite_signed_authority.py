"""A44 SQLite-backed signed checkpoint authority contract.

EXPECTED RED: the production backend does not exist.

PROPOSED API:

    SQLiteSignedCheckpointMonotonicAuthority.bootstrap(
        path=Path,
        authority_id=str,
        signer=Ed25519PrivateKey,
        root_id=str,
        root_public_key=bytes,
        enrollment_epoch=int,
        initial_revision=int,
        initial_generation=int,
        initial_fence_token=int,
    )

    SQLiteSignedCheckpointMonotonicAuthority.open(
        path=Path,
        expected_authority_id=str,
        signer=Ed25519PrivateKey,
        expected_root_id=str,
        expected_root_public_key=bytes,
        expected_enrollment_epoch=int,
    )

The resulting object implements the already established
signed checkpoint authority protocol:

    backend.hold(challenge=bytes)
        -> held (canonical_message, ed25519_signature)

    backend.advance_if_current(
        expected_revision=int,
        next_revision=int,
        expected_generation=int,
        expected_fence_token=int,
        challenge=bytes,
    ) -> signed CAS response pair

A successful CAS must atomically advance all three counters:
revision -> next_revision,
generation -> expected_generation + 1,
fence_token -> expected_fence_token + 1.

A held signed read must exclude conflicting SQLite CAS
publication until its context is released.

Messages must match the existing signed authority client's
strict canonical ASCII JSON schema and Ed25519 verification.

The signing key is supplied by the caller and is not stored
as private key material inside the database.

SECURITY LIMITATIONS:

- This is a LOCAL SQLite-backed reference implementation.
- Ordinary reopen persistence is NOT full rollback resistance.
- A valid older complete database copy may replace the file.
- Caller-provided public key pins are not independently enrolled.
- No real network service, transport security or remote lease.
- No power-loss durability guarantee is established by tests.
- No cross-system checkpoint publication atomicity.
- No hardware security module or trusted monotonic counter.
- No restore/republication authorization.
- Python objects are not an in-process security boundary.

Tests use isolated temporary databases and throwaway keys.
No production checkpoint or persisted signing key is touched.
"""

import importlib
import json
import os
import shutil
import sqlite3
import tempfile
import unittest

from contextlib import closing
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from core.existence.history_receipt_trust_checkpoint_external_monotonic_authority import (
    SignedCheckpointExternalMonotonicAuthoritySource,
)

from test_a44_checkpoint_external_monotonic_authority import (
    AUTHORITY_ID,
    ROOT,
    ROOT_KEY,
    EPOCH,
    OLD,
    NEXT,
    GENERATION,
    FENCE,
    DOMAIN,
    canonical,
    public_bytes,
)


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_sqlite_signed_authority"
)

CHALLENGE = bytes(range(32, 64))


class A44CheckpointSQLiteSignedAuthorityContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.backend_type = (
            module.SQLiteSignedCheckpointMonotonicAuthority
        )

        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

        self.path = (
            Path(self.folder.name)
            / "signed-authority.sqlite3"
        )

        self.signer = Ed25519PrivateKey.generate()

        self.public_key = public_bytes(
            self.signer
        )

    def bootstrap(self, **changes):
        arguments = {
            "path": self.path,
            "authority_id": AUTHORITY_ID,
            "signer": self.signer,
            "root_id": ROOT,
            "root_public_key": ROOT_KEY,
            "enrollment_epoch": EPOCH,
            "initial_revision": OLD,
            "initial_generation": GENERATION,
            "initial_fence_token": FENCE,
        }

        arguments.update(changes)

        return self.backend_type.bootstrap(
            **arguments
        )

    def reopen(self, **changes):
        arguments = {
            "path": self.path,
            "expected_authority_id": AUTHORITY_ID,
            "signer": self.signer,
            "expected_root_id": ROOT,
            "expected_root_public_key": ROOT_KEY,
            "expected_enrollment_epoch": EPOCH,
        }

        arguments.update(changes)

        return self.backend_type.open(
            **arguments
        )

    def client(self, backend, **changes):
        arguments = {
            "authority": backend,
            "expected_authority_id": AUTHORITY_ID,
            "expected_authority_public_key": self.public_key,
            "expected_root_id": ROOT,
            "expected_root_public_key": ROOT_KEY,
            "expected_enrollment_epoch": EPOCH,
            "minimum_revision": OLD,
            "minimum_generation": GENERATION,
            "minimum_fence_token": FENCE,
        }

        arguments.update(changes)

        return (
            SignedCheckpointExternalMonotonicAuthoritySource
            .from_authority(**arguments)
        )

    @staticmethod
    def read(source):
        with source.hold() as snapshot:
            return snapshot

    @staticmethod
    def expected(
        revision=OLD,
        generation=GENERATION,
        fence=FENCE,
    ):
        return (
            ROOT,
            ROOT_KEY,
            EPOCH,
            revision,
            generation,
            fence,
        )

    @staticmethod
    def advance(
        client,
        *,
        old_revision=OLD,
        new_revision=NEXT,
        old_generation=GENERATION,
        old_fence=FENCE,
    ):
        return client.advance_if_current(
            expected_revision=old_revision,
            next_revision=new_revision,
            expected_generation=old_generation,
            expected_fence_token=old_fence,
        )

    def test_canonical_signed_held_read(self):
        backend = self.bootstrap()

        with backend.hold(
            challenge=CHALLENGE
        ) as pair:
            self.assertIs(type(pair), tuple)
            self.assertEqual(len(pair), 2)

            message, signature = pair

            self.assertIs(type(message), bytes)
            self.assertIs(type(signature), bytes)
            self.assertEqual(len(signature), 64)

            document = json.loads(
                message.decode("ascii")
            )

            self.assertEqual(
                message,
                canonical(document),
            )

            self.assertEqual(
                document["domain"],
                DOMAIN,
            )

            self.assertEqual(
                document["version"],
                1,
            )

            self.assertEqual(
                document["operation"],
                "read",
            )

            self.assertEqual(
                document["authority_id"],
                AUTHORITY_ID,
            )

            self.assertEqual(
                document["root_id"],
                ROOT,
            )

            self.assertEqual(
                document["root_public_key_hex"],
                ROOT_KEY.hex(),
            )

            self.assertEqual(
                document["enrollment_epoch"],
                EPOCH,
            )

            self.assertEqual(
                document["revision"],
                OLD,
            )

            self.assertEqual(
                document["generation"],
                GENERATION,
            )

            self.assertEqual(
                document["fence_token"],
                FENCE,
            )

            self.assertEqual(
                document["challenge_hex"],
                CHALLENGE.hex(),
            )

            Ed25519PublicKey.from_public_bytes(
                self.public_key
            ).verify(
                signature,
                message,
            )

        client = self.client(backend)

        self.assertEqual(
            self.read(client),
            self.expected(),
        )

    def test_signed_cas_readback_and_reopen_persist_all_counters(
        self
    ):
        backend = self.bootstrap()
        client = self.client(backend)

        published = self.advance(client)

        self.assertEqual(
            published,
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

        reopened = self.reopen()

        reopened_client = self.client(
            reopened
        )

        self.assertEqual(
            self.read(reopened_client),
            published,
        )

        self.assertEqual(
            self.advance(
                reopened_client,
                old_revision=NEXT,
                new_revision=NEXT + 1,
                old_generation=GENERATION + 1,
                old_fence=FENCE + 1,
            ),
            self.expected(
                NEXT + 1,
                GENERATION + 2,
                FENCE + 2,
            ),
        )

        self.assertEqual(
            self.read(self.client(self.reopen())),
            self.expected(
                NEXT + 1,
                GENERATION + 2,
                FENCE + 2,
            ),
        )

    def test_rebootstrap_never_overwrites_existing_store(
        self
    ):
        self.bootstrap()

        before = self.path.read_bytes()

        with self.assertRaises(ValueError):
            self.bootstrap(
                initial_revision=OLD - 1,
            )

        self.assertEqual(
            self.path.read_bytes(),
            before,
        )

        self.assertEqual(
            self.read(self.client(self.reopen())),
            self.expected(),
        )

    def test_invalid_bootstrap_does_not_create_store(
        self
    ):
        attacks = (
            {"authority_id": ""},
            {"authority_id": True},
            {"authority_id": " invalid"},
            {"signer": None},
            {"signer": object()},
            {"root_id": ""},
            {"root_id": True},
            {"root_public_key": b"short"},
            {
                "root_public_key":
                    bytearray(ROOT_KEY)
            },
            {"enrollment_epoch": True},
            {"enrollment_epoch": -1},
            {"initial_revision": True},
            {"initial_revision": -1},
            {"initial_generation": True},
            {"initial_generation": -1},
            {"initial_fence_token": True},
            {"initial_fence_token": -1},
        )

        for index, changes in enumerate(attacks):
            with self.subTest(
                index=index,
                changes=repr(changes)[:80],
            ):
                invalid_path = (
                    Path(self.folder.name)
                    / f"invalid-{index}.sqlite3"
                )

                with self.assertRaises(ValueError):
                    self.bootstrap(
                        path=invalid_path,
                        **changes,
                    )

                self.assertFalse(
                    invalid_path.exists()
                )

        self.assertFalse(
            self.path.exists()
        )

    def test_reopen_rejects_wrong_identity_keys_and_epoch(
        self
    ):
        self.bootstrap()

        wrong_signer = (
            Ed25519PrivateKey.generate()
        )

        invalid = (
            {"expected_authority_id": "foreign"},
            {"expected_authority_id": True},
            {"expected_root_id": "foreign"},
            {"expected_root_id": True},
            {"expected_root_public_key": b"\x42" * 32},
            {
                "expected_root_public_key":
                    bytearray(ROOT_KEY)
            },
            {"expected_enrollment_epoch": EPOCH + 1},
            {"expected_enrollment_epoch": True},
            {"signer": wrong_signer},
            {"signer": object()},
        )

        for changes in invalid:
            with self.subTest(
                changes=repr(changes)[:100],
            ):
                with self.assertRaises(ValueError):
                    self.reopen(
                        **changes
                    )

        self.assertEqual(
            self.read(self.client(self.reopen())),
            self.expected(),
        )

    def test_missing_corrupt_and_wal_database_fail_closed(
        self
    ):
        with self.assertRaises(ValueError):
            self.reopen()

        self.assertFalse(
            self.path.exists()
        )

        self.path.write_bytes(
            b"not-a-sqlite-database"
        )

        with self.assertRaises(ValueError):
            self.reopen()

        wal_path = (
            Path(self.folder.name)
            / "wal-signed-authority.sqlite3"
        )

        self.bootstrap(
            path=wal_path
        )

        with closing(sqlite3.connect(wal_path)) as connection:
            mode = connection.execute(
                "PRAGMA journal_mode=WAL"
            ).fetchone()[0]

            self.assertEqual(
                mode.lower(),
                "wal",
            )

        with self.assertRaises(ValueError):
            self.reopen(
                path=wal_path
            )

        self.assertTrue(
            wal_path.exists()
        )

    def test_two_handles_reject_stale_cas(
        self
    ):
        first = self.bootstrap()
        second = self.reopen()

        first_client = self.client(first)
        second_client = self.client(second)

        self.assertEqual(
            self.advance(first_client),
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

        with self.assertRaises(ValueError):
            self.advance(
                second_client,
                old_revision=OLD,
                new_revision=NEXT + 1,
            )

        self.assertEqual(
            self.read(second_client),
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

        self.assertEqual(
            self.advance(
                second_client,
                old_revision=NEXT,
                new_revision=NEXT + 1,
                old_generation=GENERATION + 1,
                old_fence=FENCE + 1,
            ),
            self.expected(
                NEXT + 1,
                GENERATION + 2,
                FENCE + 2,
            ),
        )

    def test_invalid_challenge_and_cas_inputs_do_not_mutate(
        self
    ):
        backend = self.bootstrap()

        invalid_challenges = (
            None,
            True,
            b"",
            b"short",
            b"\x00" * 31,
            bytearray(CHALLENGE),
            "not-bytes",
        )

        for challenge in invalid_challenges:
            with self.subTest(
                challenge=repr(challenge)[:55],
            ):
                with self.assertRaises(ValueError):
                    with backend.hold(
                        challenge=challenge
                    ):
                        pass

                with self.assertRaises(ValueError):
                    backend.advance_if_current(
                        expected_revision=OLD,
                        next_revision=NEXT,
                        expected_generation=GENERATION,
                        expected_fence_token=FENCE,
                        challenge=challenge,
                    )

        invalid_preconditions = (
            {"expected_revision": OLD - 1},
            {"expected_revision": True},
            {"next_revision": OLD},
            {"next_revision": True},
            {"next_revision": -1},
            {"expected_generation": GENERATION - 1},
            {"expected_generation": True},
            {"expected_fence_token": FENCE - 1},
            {"expected_fence_token": True},
        )

        for changes in invalid_preconditions:
            with self.subTest(
                changes=changes
            ):
                arguments = {
                    "expected_revision": OLD,
                    "next_revision": NEXT,
                    "expected_generation": GENERATION,
                    "expected_fence_token": FENCE,
                    "challenge": CHALLENGE,
                }

                arguments.update(changes)

                with self.assertRaises(ValueError):
                    backend.advance_if_current(
                        **arguments
                    )

        self.assertEqual(
            self.read(self.client(backend)),
            self.expected(),
        )

    def test_held_signed_read_excludes_conflicting_cas(
        self
    ):
        first = self.bootstrap()
        second = self.reopen()

        source = self.client(first)

        with source.hold() as snapshot:
            self.assertEqual(
                snapshot,
                self.expected(),
            )

            with self.assertRaises(ValueError):
                second.advance_if_current(
                    expected_revision=OLD,
                    next_revision=NEXT,
                    expected_generation=GENERATION,
                    expected_fence_token=FENCE,
                    challenge=CHALLENGE,
                )

            self.assertEqual(
                snapshot[3:],
                (
                    OLD,
                    GENERATION,
                    FENCE,
                ),
            )

        self.assertEqual(
            self.advance(
                self.client(second)
            ),
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

    def test_caller_failure_releases_held_transaction(
        self
    ):
        first = self.bootstrap()
        second = self.reopen()

        client = self.client(first)

        with self.assertRaises(ValueError):
            with client.hold():
                raise ValueError(
                    "Injected caller verification failure."
                )

        self.assertEqual(
            self.advance(
                self.client(second)
            ),
            self.expected(
                NEXT,
                GENERATION + 1,
                FENCE + 1,
            ),
        )

    def test_full_file_rollback_remains_possible(
        self
    ):
        backend = self.bootstrap()

        older = (
            Path(self.folder.name)
            / "older-valid-authority.sqlite3"
        )

        shutil.copyfile(
            self.path,
            older,
        )

        client = self.client(backend)

        self.advance(client)

        self.assertEqual(
            self.read(self.client(self.reopen()))[3],
            NEXT,
        )

        # Simulated complete-file rollback.
        # This is a known SQLite trust limitation.
        shutil.copyfile(
            older,
            self.path,
        )

        reopened = self.reopen()

        self.assertEqual(
            self.read(self.client(reopened)),
            self.expected(),
        )

        higher = self.client(
            reopened,
            minimum_revision=NEXT,
            minimum_generation=GENERATION + 1,
            minimum_fence_token=FENCE + 1,
        )

        with self.assertRaises(ValueError):
            self.read(higher)

        self.assertEqual(
            self.read(self.client(reopened)),
            self.expected(),
        )

    def test_caller_repinning_is_not_independent_enrollment(
        self
    ):
        self.bootstrap()

        rogue_signer = (
            Ed25519PrivateKey.generate()
        )

        rogue_path = (
            Path(self.folder.name)
            / "caller-repinned-authority.sqlite3"
        )

        rogue = self.bootstrap(
            path=rogue_path,
            signer=rogue_signer,
        )

        old_pin = self.client(
            rogue
        )

        with self.assertRaises(ValueError):
            self.read(old_pin)

        new_pin = self.client(
            rogue,
            expected_authority_public_key=(
                public_bytes(rogue_signer)
            ),
        )

        self.assertEqual(
            self.read(new_pin),
            self.expected(),
        )

        for name in (
            "restore",
            "republish",
            "authorize",
            "publish",
        ):
            with self.subTest(operation=name):
                self.assertFalse(
                    hasattr(rogue, name)
                )


if __name__ == "__main__":
    unittest.main()
