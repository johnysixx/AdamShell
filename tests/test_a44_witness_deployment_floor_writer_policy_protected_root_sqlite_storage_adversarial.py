"""Adversarial SQLite protected root storage tests.

All corruption is confined to temporary test databases.

These tests exercise fail-closed handling of malformed records,
incorrect pairings, invalid object inputs and filesystem aliases.

The complete trusted storage pair remains the trust boundary.
Replacing that pair is not claimed to be prevented.
"""

import hashlib
import json
import os
import sqlite3
import unittest

from contextlib import closing
from dataclasses import replace

import test_a44_witness_deployment_floor_writer_policy_protected_root_sqlite_contract as previous


class A44SQLiteProtectedRootStorageAdversarialTests(unittest.TestCase):

    def setUp(self):

        self.f = previous.A44SQLiteProtectedRootContractTests(
            "test_01_explicit_create_and_unprovisioned_open"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.backend = self.f.backend
        self.objects = self.f.f
        self.identity = self.f.identity
        self.initial = self.f.initial
        self.path = self.f.path
        self.fence = self.f.fence_path

    def sql(self, path, statement, parameters=()):

        with closing(
            sqlite3.connect(
                path.as_uri() + "?mode=rw",
                uri=True,
                timeout=10,
            )
        ) as connection:

            cursor = connection.execute(
                statement,
                parameters,
            )

            rows = cursor.fetchall()

            connection.commit()

            return rows

    def payload(self):

        rows = self.sql(
            self.path,
            "SELECT payload FROM root_state",
        )

        self.assertEqual(len(rows), 1)

        return rows[0][0]

    def store_payload(self, payload):

        digest = hashlib.sha256(payload).hexdigest()

        self.sql(
            self.path,
            "UPDATE root_state SET payload=?, digest=?",
            (payload, digest),
        )

    def store_fields(self, fields):

        self.store_payload(
            json.dumps(
                fields,
                ensure_ascii=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )

    def prepare(self):

        self.f.provision()

        pending = self.objects.pending()

        self.f.advance(self.initial, pending)

        self.f.assert_state(self.backend, pending)

        return pending

    def snapshot_pair(self):

        return (
            self.path.read_bytes(),
            self.fence.read_bytes(),
        )

    def assert_closed(self):

        before = self.snapshot_pair()

        for operation in (
            self.backend.read,
            self.f.reopen,
            lambda: self.backend.provision(state=self.initial),
            lambda: self.backend.compare_and_set(
                expected=self.initial.reference(),
                replacement=self.objects.pending(),
            ),
        ):

            with self.assertRaises(ValueError):
                operation()

        with self.assertRaises(ValueError):

            with self.backend.exclusive():

                self.fail(
                    "Invalid protected storage entered fence"
                )

        self.assertEqual(
            self.snapshot_pair(),
            before,
            "Rejected operations mutated protected storage",
        )

    def test_01_corrupted_payload_digest_rejected(self):

        self.f.provision()

        self.sql(
            self.path,
            "UPDATE root_state SET payload=?",
            (b"corrupted",),
        )

        self.assert_closed()

    def test_02_noncanonical_payload_with_valid_digest_rejected(self):

        self.f.provision()

        payload = self.payload()

        self.store_payload(payload + b" ")

        self.assert_closed()

    def test_03_canonical_wrong_identity_rejected(self):

        self.f.provision()

        fields = json.loads(self.payload())

        self.assertEqual(
            fields[3],
            self.identity.provisioning_nonce.hex(),
        )

        fields[3] = b"x".hex() * 32

        self.store_fields(fields)

        self.assert_closed()

    def test_04_prepared_message_digest_mismatch_rejected(self):

        pending = self.prepare()

        fields = json.loads(self.payload())

        self.assertEqual(
            bytes.fromhex(fields[7][4]),
            pending.durable_state.prepared.signed_policy[0],
        )

        fields[7][4] = b"substituted-candidate".hex()

        self.store_fields(fields)

        self.assert_closed()

    def test_05_invalid_prepared_signature_length_rejected(self):

        self.prepare()

        fields = json.loads(self.payload())

        fields[7][5] = (b"s" * 63).hex()

        self.store_fields(fields)

        self.assert_closed()

    def test_06_missing_state_singleton_rejected(self):

        self.f.provision()

        self.sql(
            self.path,
            "DELETE FROM root_state",
        )

        self.assert_closed()

    def test_07_unexpected_state_schema_rejected(self):

        self.f.provision()

        self.sql(
            self.path,
            "CREATE TABLE unexpected_state (value TEXT)",
        )

        self.assert_closed()

    def test_08_unexpected_fence_schema_rejected(self):

        self.f.provision()

        self.sql(
            self.fence,
            "CREATE TABLE unexpected_fence (value TEXT)",
        )

        self.assert_closed()

    def test_09_swapped_database_roles_rejected(self):

        self.f.provision()

        state, fence = self.snapshot_pair()

        self.path.write_bytes(fence)
        self.fence.write_bytes(state)

        self.assert_closed()

    def test_10_same_identity_foreign_fence_rejected(self):

        retained = self.prepare()

        alternate = self.f.directory / "foreign.sqlite3"

        self.f.create(path=alternate)

        alternate_fence = alternate.with_name(
            alternate.name + ".fence.sqlite3"
        )

        original_fence = self.fence.read_bytes()

        self.fence.write_bytes(
            alternate_fence.read_bytes()
        )

        self.assert_closed()

        self.fence.write_bytes(original_fence)

        self.f.assert_state(
            self.f.reopen(),
            retained,
        )

    def assert_hardlink_rejected(self, target):

        self.f.provision()

        alias = self.f.directory / "alias.sqlite3"

        os.link(target, alias)

        try:

            self.assertTrue(
                os.path.samefile(target, alias)
            )

            self.assertEqual(
                target.stat().st_nlink,
                2,
            )

            self.assert_closed()

        finally:

            alias.unlink()

        self.f.assert_state(
            self.f.reopen(),
            self.initial,
        )

    def test_11_state_hardlink_alias_rejected(self):

        self.assert_hardlink_rejected(self.path)

    def test_12_fence_hardlink_alias_rejected(self):

        self.assert_hardlink_rejected(self.fence)

    def test_13_complete_pair_replacement_trust_boundary(self):

        pending = self.prepare()

        final = self.objects.finalized(pending)

        self.f.advance(pending, final)

        self.f.assert_state(self.backend, final)

        alternate = self.f.directory / "replacement.sqlite3"

        replacement = self.f.create(path=alternate)

        replacement.provision(state=self.initial)

        alternate_fence = alternate.with_name(
            alternate.name + ".fence.sqlite3"
        )

        self.path.write_bytes(
            alternate.read_bytes()
        )

        self.fence.write_bytes(
            alternate_fence.read_bytes()
        )

        # An existing handle pins its original storage ID.

        with self.assertRaises(ValueError):
            self.backend.read()

        with self.assertRaises(ValueError):

            with self.backend.exclusive():

                self.fail(
                    "Original handle accepted replacement storage"
                )

        # A fresh open only has the external deployment identity.
        # A completely substituted trusted pair is outside this
        # reference backend's rollback-resistance guarantee.

        fresh = self.f.reopen()

        self.assertEqual(fresh.identity, self.identity)

        self.f.assert_state(fresh, self.initial)

        self.assertNotEqual(
            fresh.read().reference(),
            final.reference(),
        )

    def test_14_invalid_provisioning_and_noncanonical_cas(self):

        initial = self.initial

        invalid_identity = replace(
            self.identity,
            provisioning_nonce=b"x" * 32,
        )

        invalid_states = (
            {},
            replace(initial, revision=2),
            self.objects.pending(),
            replace(initial, identity=invalid_identity),
        )

        before = self.snapshot_pair()

        for invalid in invalid_states:

            with self.assertRaises(ValueError):

                self.backend.provision(state=invalid)

            self.assertEqual(
                self.snapshot_pair(),
                before,
            )

            with self.assertRaises(ValueError):
                self.backend.read()

        self.f.provision()

        pending = self.objects.pending()

        before = self.snapshot_pair()

        for expected, replacement in (
            ({}, pending),
            (initial.reference(), {}),
            (initial.reference(), None),
        ):

            with self.assertRaises(ValueError):

                self.backend.compare_and_set(
                    expected=expected,
                    replacement=replacement,
                )

            self.assertEqual(
                self.snapshot_pair(),
                before,
            )

        self.f.assert_state(self.backend, initial)

        self.f.advance(initial, pending)

        self.f.assert_state(self.f.reopen(), pending)

    def test_15_nested_independent_instances_share_same_fence(self):

        self.f.provision()

        peer = self.f.reopen()

        self.assertIsNot(peer, self.backend)

        pending = self.objects.pending()
        final = self.objects.finalized(pending)

        with self.assertRaises(OSError):

            with self.backend.exclusive():

                with peer.exclusive():

                    self.f.assert_state(peer, self.initial)

                    self.f.advance(
                        self.initial,
                        pending,
                        backend=peer,
                    )

                    self.f.assert_state(
                        self.backend,
                        pending,
                    )

                    self.f.advance(
                        pending,
                        final,
                    )

                self.f.assert_state(peer, final)

                raise OSError(
                    "Injected outer operation failure"
                )

        self.f.assert_state(
            self.f.reopen(),
            final,
        )

    def test_16_incomplete_storage_never_reinitialized(self):

        for name, role in (
            ("partial-state.sqlite3", "state"),
            ("partial-fence.sqlite3", "fence"),
        ):

            path = self.f.directory / name

            fence = path.with_name(
                path.name + ".fence.sqlite3"
            )

            present = path if role == "state" else fence

            missing = fence if role == "state" else path

            present.write_bytes(b"incomplete-storage")

            before = present.read_bytes()

            with self.assertRaises(ValueError):
                self.f.reopen(path=path)

            with self.assertRaises(ValueError):
                self.f.create(path=path)

            self.assertEqual(
                present.read_bytes(),
                before,
            )

            self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
