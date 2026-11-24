"""A44 / 66.39B: persistent signed writer-policy authority contract.

Production API:

SQLitePersistentWriterPolicyAuthority.create(
    *,
    path,
    backend,
    expected_policy_id,
    expected_policy_public_key,
    signed_genesis_policy,
    expected_genesis_sha256,
)

SQLitePersistentWriterPolicyAuthority.open(
    *,
    path,
    backend,
    expected_policy_id,
    expected_policy_public_key,
    expected_genesis_sha256,
    minimum_policy_epoch=1,
    expected_current_policy_sha256=None,
)

authority.publish_policy(*, signed_policy)
authority.current_policy_reference() -> tuple[int, str]
authority.retired_writer_keys() -> tuple[bytes, ...]

PersistentWriterPolicyGateway.from_authority(*, authority)
gateway.exchange(request: bytes) -> bytes

The existing signed policy v1 and authorized CAS v2 formats are retained.

CREATE is explicit and must never overwrite an existing database.
OPEN must never initialize a missing or empty policy store.
Bootstrap requires an exact externally pinned signed genesis digest.
The complete retained history must be validated from genesis.

Each policy publication must atomically persist its signed document and
advance the current head. Retired keys must be derived from or verified
against the complete authenticated policy history.

Retired keys include:
- replaced writer keys;
- removed writer keys;
- revoked writer keys.

A retired key cannot become active again under any identity.
A key cannot be transferred between identities in one transition.
A newly revoked existing identity must retain its existing key.
Revocation tombstones and their keys remain permanently retained.
Keeping a revoked key in its original tombstone is not reenrollment.

The policy store is separate from the existing floor SQLite database.
Every authorized CAS and policy publication must serialize through
the same policy-store transaction boundary, across separate instances.
The policy transaction lock remains held through backend CAS execution.
A stale policy must never be used by a cooperating persistent gateway.

Required history table:
    writer_policy_history
        policy_epoch
        message
        signature

Required current-head table:
    writer_policy_head

Publication updates both history and head in one SQLite transaction.

Public READ and LOOKUP preserve the existing signed wire protocol.

This reference does not fence old v1 or in-memory gateways, arbitrary
direct backend access, separate policy-store copies, whole-database
rollback without external retained pins, or malicious in-process code.

It does not claim a distributed transaction across both databases.
"""


import importlib
import sqlite3
import sys
import tempfile
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_witness_deployment_floor_writer_policy_contract as policy


remote = policy.remote

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_sqlite_reference"
)


class A44PersistentWriterPolicyContractTests(unittest.TestCase):

    def setUp(self):

        module = importlib.import_module(MODULE)

        self.authority_type = (
            module.SQLitePersistentWriterPolicyAuthority
        )

        self.gateway_type = (
            module.PersistentWriterPolicyGateway
        )

        self.p = policy.A44VersionedWriterPolicyContractTests(
            "test_01_signed_policy_bootstrap_and_authorized_cas"
        )

        self.addCleanup(
            self.p.doCleanups,
        )

        self.p.setUp()

        temporary = tempfile.TemporaryDirectory(
            prefix="a44-writer-policy-",
        )

        self.addCleanup(
            temporary.cleanup,
        )

        self.directory = Path(temporary.name)

        self.path = (
            self.directory / "writer-policy.sqlite3"
        )

        self.genesis = self.p.initial

        self.genesis_sha = policy.digest(
            self.genesis,
        )

        self.authority = self.create()

        self.gateway = self.make_gateway()


    def create(self, **changes):

        params = {
            "path": self.path,
            "backend": self.p.backend,
            "expected_policy_id": policy.POLICY_ID,
            "expected_policy_public_key": self.p.root_key,
            "signed_genesis_policy": self.genesis,
            "expected_genesis_sha256": self.genesis_sha,
        }

        params.update(changes)

        return self.authority_type.create(
            **params,
        )


    def reopen(self, **changes):

        params = {
            "path": self.path,
            "backend": self.p.backend,
            "expected_policy_id": policy.POLICY_ID,
            "expected_policy_public_key": self.p.root_key,
            "expected_genesis_sha256": self.genesis_sha,
            "minimum_policy_epoch": 1,
            "expected_current_policy_sha256": None,
        }

        params.update(changes)

        return self.authority_type.open(
            **params,
        )


    def make_gateway(self, authority=None):

        if authority is None:
            authority = self.authority

        return self.gateway_type.from_authority(
            authority=authority,
        )


    def reference(self, signed_policy, epoch):

        return (
            epoch,
            policy.digest(signed_policy),
        )


    def assert_reference(
        self,
        signed_policy,
        epoch,
        authority=None,
    ):

        if authority is None:
            authority = self.authority

        self.assertEqual(
            authority.current_policy_reference(),
            self.reference(signed_policy, epoch),
        )


    def publish(self, signed_policy, authority=None):

        if authority is None:
            authority = self.authority

        return authority.publish_policy(
            signed_policy=signed_policy,
        )


    def send(
        self,
        signed_policy=None,
        gateway=None,
        **changes,
    ):

        if signed_policy is None:
            signed_policy = self.genesis

        if gateway is None:
            gateway = self.gateway

        request = self.p.authorized(
            policy=signed_policy,
            **changes,
        )

        return self.p.send(
            request,
            gateway=gateway,
        )


    def operation_count(self):

        return (
            self.p.f.fixture.fixture.operation_count()
        )


    def history(self, path=None):

        if path is None:
            path = self.path

        with closing(
            sqlite3.connect(
                path.resolve().as_uri() + "?mode=ro",
                uri=True,
            )
        ) as connection:

            return tuple(
                connection.execute(
                    "SELECT policy_epoch, message, signature "
                    "FROM writer_policy_history "
                    "ORDER BY policy_epoch"
                ).fetchall()
            )


    def assert_history(self, *signed_policies):

        expected = tuple(
            (epoch, pair[0], pair[1])
            for epoch, pair in enumerate(
                signed_policies,
                start=1,
            )
        )

        self.assertEqual(
            self.history(),
            expected,
        )


    def execute_sql(self, statement, parameters=()):

        with closing(
            sqlite3.connect(
                str(self.path),
                timeout=5,
            )
        ) as connection:

            with connection:

                connection.execute(
                    statement,
                    parameters,
                )


    def backup(self, destination):

        with closing(
            sqlite3.connect(str(self.path))
        ) as source:

            with closing(
                sqlite3.connect(str(destination))
            ) as target:

                source.backup(target)


    def restore_backup(self, source_path):

        with closing(
            sqlite3.connect(str(source_path))
        ) as source:

            with closing(
                sqlite3.connect(str(self.path))
            ) as target:

                source.backup(target)


    def test_01_create_persists_exact_signed_genesis(self):

        self.assertTrue(
            self.path.is_file()
        )

        self.assert_reference(
            self.genesis,
            1,
        )

        self.assert_history(
            self.genesis,
        )

        self.assertEqual(
            self.authority.retired_writer_keys(),
            (),
        )

        self.p.unchanged()

        result = self.send()

        self.assertEqual(
            (result["status"], result["epoch"]),
            ("committed", 2),
        )


    def test_02_create_never_overwrites_existing_policy_database(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        with self.assertRaises(ValueError):
            self.create()

        self.assert_reference(second, 2)

        self.assert_history(
            self.genesis,
            second,
        )

        self.p.unchanged()


    def test_03_open_never_initializes_missing_or_empty_database(self):

        missing = (
            self.directory / "missing.sqlite3"
        )

        empty = (
            self.directory / "empty.sqlite3"
        )

        empty.touch()

        for path in (missing, empty):

            with self.subTest(path=path.name):

                with self.assertRaises(ValueError):

                    self.reopen(path=path)

        self.assertFalse(
            missing.exists()
        )

        self.assertEqual(
            empty.read_bytes(),
            b"",
        )

        self.assert_history(
            self.genesis,
        )


    def test_04_policy_store_must_not_alias_floor_database(self):

        floor_path = Path(
            self.p.f.fixture.fixture.path
        ).resolve()

        for action in (
            self.create,
            self.reopen,
        ):

            with self.subTest(action=action.__name__):

                with self.assertRaises(ValueError):

                    action(path=floor_path)

        self.p.unchanged()

        self.assert_history(
            self.genesis,
        )


    def test_05_reopen_recovers_latest_policy_and_revocation(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        reopened = self.reopen()

        self.assertIsNot(
            reopened,
            self.authority,
        )

        self.assert_reference(
            second,
            2,
            authority=reopened,
        )

        gateway = self.make_gateway(
            reopened,
        )

        for signed_policy in (
            self.genesis,
            second,
        ):

            with self.assertRaises(ValueError):

                self.send(
                    signed_policy,
                    gateway=gateway,
                )

        self.p.unchanged()

        result = self.send(
            second,
            gateway=gateway,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )


    def test_06_independent_live_authorities_share_current_policy(self):

        independent = self.reopen()

        old_gateway = self.make_gateway(
            independent,
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        self.assert_reference(
            second,
            2,
            authority=independent,
        )

        for signed_policy in (
            self.genesis,
            second,
        ):

            with self.assertRaises(ValueError):

                self.send(
                    signed_policy,
                    gateway=old_gateway,
                )

        self.p.unchanged()

        result = self.send(
            second,
            gateway=old_gateway,
            writer_id="writer-beta",
            signer=self.p.f.bob,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )


    def test_07_conflicting_signed_publications_have_exactly_one_winner(self):

        independent = self.reopen()

        first = self.p.next_policy()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        barrier = threading.Barrier(2)

        def attempt(authority, candidate):

            barrier.wait(timeout=5)

            try:

                self.publish(
                    candidate,
                    authority=authority,
                )

            except ValueError:

                return None

            return candidate

        with ThreadPoolExecutor(max_workers=2) as pool:

            a = pool.submit(
                attempt,
                self.authority,
                first,
            )

            b = pool.submit(
                attempt,
                independent,
                second,
            )

            results = (
                a.result(timeout=15),
                b.result(timeout=15),
            )

        winners = [
            item
            for item in results
            if item is not None
        ]

        self.assertEqual(
            len(winners),
            1,
        )

        winner = winners[0]

        self.assert_reference(winner, 2)

        self.assert_reference(
            winner,
            2,
            authority=independent,
        )

        self.assert_history(
            self.genesis,
            winner,
        )

        self.p.unchanged()


    def test_08_policy_root_genesis_pin_and_identity_are_required(self):

        invalid_open = (
            {
                "expected_policy_public_key":
                    policy.public_key(self.p.f.attacker),
            },
            {
                "expected_genesis_sha256":
                    "ab" * 32,
            },
            {
                "expected_policy_id":
                    "different-policy",
            },
        )

        for changes in invalid_open:

            with self.subTest(changes=repr(changes)):

                with self.assertRaises(ValueError):

                    self.reopen(**changes)

        wrong_genesis = self.p.policy(
            signer=self.p.f.attacker,
        )

        invalid_path = (
            self.directory / "invalid-genesis.sqlite3"
        )

        with self.assertRaises(ValueError):

            self.create(
                path=invalid_path,
                signed_genesis_policy=wrong_genesis,
                expected_genesis_sha256=policy.digest(
                    wrong_genesis
                ),
            )

        self.assertFalse(
            invalid_path.exists()
        )

        self.assert_history(
            self.genesis,
        )


    def test_09_external_retained_epoch_and_current_digest_are_enforced(self):

        second = self.p.next_policy()

        self.publish(second)

        reopened = self.reopen(
            minimum_policy_epoch=2,
            expected_current_policy_sha256=policy.digest(
                second,
            ),
        )

        self.assert_reference(
            second,
            2,
            authority=reopened,
        )

        for changes in (
            {"minimum_policy_epoch": 3},
            {"minimum_policy_epoch": True},
            {"minimum_policy_epoch": 0},
            {
                "expected_current_policy_sha256":
                    self.genesis_sha,
            },
        ):

            with self.subTest(changes=changes):

                with self.assertRaises(ValueError):

                    self.reopen(**changes)

        self.assert_history(
            self.genesis,
            second,
        )


    def test_10_invalid_policy_transition_never_changes_history(self):

        invalid = (
            self.p.next_policy(
                signer=self.p.f.attacker,
            ),
            self.p.next_policy(epoch=3),
            self.p.policy(
                epoch=2,
                previous="ab" * 32,
            ),
            self.genesis,
        )

        for candidate in invalid:

            with self.subTest(
                candidate=policy.digest(candidate),
            ):

                with self.assertRaises(ValueError):

                    self.publish(candidate)

                self.assert_reference(
                    self.genesis,
                    1,
                )

                self.assert_history(
                    self.genesis,
                )

                self.assertEqual(
                    self.authority.retired_writer_keys(),
                    (),
                )

        valid = self.p.next_policy()

        self.publish(valid)

        self.assert_history(
            self.genesis,
            valid,
        )

        self.p.unchanged()


    def test_11_rotated_key_remains_retired_after_reopen(self):

        original_key = policy.public_key(
            self.p.f.alice,
        )

        writers = dict(
            self.p.f.writer_keys,
        )

        writers["writer-alpha"] = policy.public_key(
            self.p.f.attacker,
        )

        second = self.p.next_policy(
            writers=writers,
        )

        self.publish(second)

        reopened = self.reopen()

        self.assertEqual(
            reopened.retired_writer_keys(),
            (original_key,),
        )

        writers["writer-charlie"] = original_key

        third = self.p.next_policy(
            second,
            writers=writers,
        )

        with self.assertRaises(ValueError):

            self.publish(
                third,
                authority=reopened,
            )

        self.assert_history(
            self.genesis,
            second,
        )

        gateway = self.make_gateway(
            reopened,
        )

        result = self.send(
            second,
            gateway=gateway,
            signer=self.p.f.attacker,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )


    def test_12_removed_writer_key_cannot_be_reenrolled(self):

        old_key = policy.public_key(
            self.p.f.alice,
        )

        remaining = {
            "writer-beta":
                policy.public_key(self.p.f.bob),
        }

        second = self.p.next_policy(
            writers=remaining,
        )

        self.publish(second)

        reopened = self.reopen()

        self.assertIn(
            old_key,
            reopened.retired_writer_keys(),
        )

        for identity in (
            "writer-alpha",
            "writer-charlie",
        ):

            with self.subTest(identity=identity):

                candidate = self.p.next_policy(
                    second,
                    writers={
                        **remaining,
                        identity: old_key,
                    },
                )

                with self.assertRaises(ValueError):

                    self.publish(
                        candidate,
                        authority=reopened,
                    )

        self.assert_history(
            self.genesis,
            second,
        )

        self.p.unchanged()


    def test_13_revoked_keys_and_tombstones_remain_permanent(self):

        old_key = policy.public_key(
            self.p.f.alice,
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        reopened = self.reopen()

        self.assertIn(
            old_key,
            reopened.retired_writer_keys(),
        )

        changed = dict(
            self.p.f.writer_keys,
        )

        changed["writer-alpha"] = policy.public_key(
            self.p.f.attacker,
        )

        invalid = (
            self.p.next_policy(
                second,
                revoked=(),
            ),
            self.p.next_policy(
                second,
                writers={
                    "writer-beta":
                        policy.public_key(self.p.f.bob),
                },
                revoked=(),
            ),
            self.p.next_policy(
                second,
                writers=changed,
            ),
        )

        for candidate in invalid:

            with self.assertRaises(ValueError):

                self.publish(
                    candidate,
                    authority=reopened,
                )

        valid = self.p.next_policy(
            second,
        )

        self.publish(
            valid,
            authority=reopened,
        )

        self.assert_history(
            self.genesis,
            second,
            valid,
        )

        self.assertIn(
            old_key,
            self.authority.retired_writer_keys(),
        )


    def test_14_simultaneous_rotation_revocation_and_reassignment_rejected(self):

        original_key = policy.public_key(
            self.p.f.alice,
        )

        rotated = dict(
            self.p.f.writer_keys,
        )

        rotated["writer-alpha"] = policy.public_key(
            self.p.f.attacker,
        )

        reassigned = {
            **rotated,
            "writer-charlie": original_key,
        }

        invalid = (
            self.p.next_policy(
                writers=rotated,
                revoked=("writer-alpha",),
            ),
            self.p.next_policy(
                writers=reassigned,
                revoked=("writer-alpha",),
            ),
        )

        for candidate in invalid:

            with self.assertRaises(ValueError):

                self.publish(candidate)

            self.assert_reference(
                self.genesis,
                1,
            )

            self.assert_history(
                self.genesis,
            )

        self.assertEqual(
            self.authority.retired_writer_keys(),
            (),
        )

        self.p.unchanged()


    def test_15_same_transition_key_transfer_is_rejected(self):

        original_key = policy.public_key(
            self.p.f.alice,
        )

        replacement_key = policy.public_key(
            self.p.f.attacker,
        )

        invalid_rosters = (
            {
                "writer-beta":
                    policy.public_key(self.p.f.bob),
                "writer-charlie":
                    original_key,
            },
            {
                "writer-alpha":
                    replacement_key,
                "writer-beta":
                    policy.public_key(self.p.f.bob),
                "writer-charlie":
                    original_key,
            },
            {
                "writer-alpha":
                    policy.public_key(self.p.f.bob),
                "writer-beta":
                    original_key,
            },
        )

        for roster in invalid_rosters:

            with self.subTest(roster=tuple(roster)):

                candidate = self.p.next_policy(
                    writers=roster,
                )

                with self.assertRaises(ValueError):

                    self.publish(candidate)

                self.assert_history(
                    self.genesis,
                )

        self.assertEqual(
            self.authority.retired_writer_keys(),
            (),
        )

        self.p.unchanged()


    def test_16_history_and_head_publication_roll_back_together(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.execute_sql(
            """
            CREATE TRIGGER a44_fail_policy_head
            BEFORE UPDATE ON writer_policy_head
            BEGIN
                SELECT RAISE(
                    ABORT,
                    'injected policy head publication failure'
                );
            END
            """
        )

        try:

            with self.assertRaises(ValueError):

                self.publish(second)

            self.assert_reference(
                self.genesis,
                1,
            )

            self.assert_history(
                self.genesis,
            )

            self.assertEqual(
                self.authority.retired_writer_keys(),
                (),
            )

        finally:

            self.execute_sql(
                "DROP TRIGGER a44_fail_policy_head"
            )

        self.publish(second)

        reopened = self.reopen()

        self.assert_reference(
            second,
            2,
            authority=reopened,
        )

        self.assert_history(
            self.genesis,
            second,
        )


    def test_17_corrupted_historical_signature_fails_closed(self):

        second = self.p.next_policy()

        self.publish(second)

        self.execute_sql(
            "UPDATE writer_policy_history "
            "SET signature = zeroblob(64) "
            "WHERE policy_epoch = 1"
        )

        with self.assertRaises(ValueError):

            self.reopen()

        with self.assertRaises(ValueError):

            self.authority.current_policy_reference()

        with self.assertRaises(ValueError):

            self.send(second)

        self.p.unchanged()


    def test_18_independent_policy_publication_serializes_with_cas(self):

        independent = self.reopen()

        entered = threading.Event()
        release = threading.Event()

        publication_started = threading.Event()
        publication_done = threading.Event()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        backend_type = type(
            self.p.backend,
        )

        original_cas = (
            backend_type.advance_if_current
        )

        def blocking_cas(backend, **arguments):

            entered.set()

            if not release.wait(timeout=10):

                raise TimeoutError(
                    "CAS test release timed out"
                )

            return original_cas(
                backend,
                **arguments,
            )

        def publish_second():

            publication_started.set()

            try:

                self.publish(
                    second,
                    authority=independent,
                )

            finally:

                publication_done.set()

        request = self.p.authorized()

        with patch.object(
            backend_type,
            "advance_if_current",
            blocking_cas,
        ):

            with ThreadPoolExecutor(max_workers=2) as pool:

                cas_future = pool.submit(
                    self.gateway.exchange,
                    request,
                )

                try:

                    self.assertTrue(
                        entered.wait(timeout=5)
                    )

                    update_future = pool.submit(
                        publish_second,
                    )

                    self.assertTrue(
                        publication_started.wait(timeout=5)
                    )

                    self.assertFalse(
                        publication_done.wait(timeout=0.3),
                        "Policy publication escaped CAS fence",
                    )

                finally:

                    release.set()

                raw = cas_future.result(timeout=15)

                update_future.result(timeout=15)

        result = self.p.f.response(
            raw,
            operation="cas",
            challenge=b"c" * 32,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.assert_reference(second, 2)

        with self.assertRaises(ValueError):

            self.send(
                second,
                request=self.p.next_cas(),
            )

        result = self.send(
            second,
            writer_id="writer-beta",
            signer=self.p.f.bob,
            request=self.p.next_cas(),
        )

        self.assertEqual(
            (result["status"], result["epoch"]),
            ("committed", 3),
        )

        self.assertEqual(
            self.operation_count(),
            2,
        )


    def test_19_revocation_preserves_signed_lookup_and_read_recovery(self):

        request = self.p.authorized()

        result = self.p.send(
            request,
            gateway=self.gateway,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

        second = self.p.next_policy(
            revoked=(
                "writer-alpha",
                "writer-beta",
            ),
        )

        self.publish(second)

        reopened = self.reopen()

        gateway = self.make_gateway(
            reopened,
        )

        with self.assertRaises(ValueError):

            gateway.exchange(request)

        raw = gateway.exchange(
            self.p.f.request(
                "lookup",
                challenge=b"l" * 32,
            )
        )

        lookup = self.p.f.response(
            raw,
            operation="lookup",
            challenge=b"l" * 32,
        )

        self.assertEqual(
            lookup["status"],
            "committed",
        )

        client = self.p.f.fixture.make_client(
            transport=gateway,
        )

        self.assertEqual(
            self.p.f.fixture.read(client)["epoch"],
            2,
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )


    def test_20_valid_old_database_rollback_requires_external_retained_pin(self):

        snapshot = (
            self.directory / "old-policy.sqlite3"
        )

        self.backup(snapshot)

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.publish(second)

        self.assert_reference(second, 2)

        # Explicit known limit:
        # Restore an older valid policy database in a temporary
        # fixture. The floor database has not been modified.

        self.restore_backup(snapshot)

        with self.assertRaises(ValueError):

            self.reopen(
                minimum_policy_epoch=2,
            )

        with self.assertRaises(ValueError):

            self.reopen(
                expected_current_policy_sha256=policy.digest(
                    second,
                ),
            )

        # Without the retained external pin, the old database
        # is still a valid signed history rooted in genesis.

        stale = self.reopen()

        self.assert_reference(
            self.genesis,
            1,
            authority=stale,
        )

        self.assert_history(
            self.genesis,
        )

        self.p.unchanged()


if __name__ == "__main__":
    unittest.main()
