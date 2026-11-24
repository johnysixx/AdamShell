"""A44 / 66.38D: adversarial versioned writer policy regression.

Tests exercise the live shared policy authority and its existing SQLite
backend. They deliberately distinguish authority-local synchronization
from independent deployment isolation and durable rollback protection.

All signing keys and SQLite databases are temporary test fixtures.
"""

import sys
import unittest

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_witness_deployment_floor_writer_policy_contract as policy

remote = policy.remote


class A44VersionedWriterPolicyAdversarialTests(unittest.TestCase):

    def setUp(self):

        self.p = policy.A44VersionedWriterPolicyContractTests(
            "test_01_signed_policy_bootstrap_and_authorized_cas"
        )

        self.addCleanup(self.p.doCleanups)

        self.p.setUp()

    def reference(self):
        return self.p.authority.current_policy_reference()

    def assert_reference(self, signed_policy, epoch):
        self.assertEqual(
            self.reference(),
            (epoch, policy.digest(signed_policy)),
        )

    def operation_count(self):
        return self.p.f.fixture.fixture.operation_count()

    def public_lookup(self):
        raw = self.p.gateway.exchange(
            self.p.f.request(
                "lookup",
                challenge=b"l" * 32,
            )
        )

        return self.p.f.response(
            raw,
            operation="lookup",
            challenge=b"l" * 32,
        )

    def test_01_concurrent_conflicting_policy_publications_have_one_winner(self):

        first = self.p.next_policy()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        def publish(candidate):
            try:
                self.p.publish(candidate)
            except ValueError:
                return None

            return candidate

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    publish,
                    (first, second),
                )
            )

        winners = [
            result
            for result in results
            if result is not None
        ]

        self.assertEqual(len(winners), 1)

        winner = winners[0]

        self.assert_reference(winner, 2)

        self.p.unchanged()

        result = self.p.send(
            self.p.authorized(
                policy=winner,
                writer_id="writer-beta",
                signer=self.p.f.bob,
            )
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

    def test_02_duplicate_policy_publication_cannot_advance_epoch_twice(self):

        second = self.p.next_policy()

        self.p.publish(second)

        for _ in range(3):

            with self.assertRaises(ValueError):
                self.p.publish(second)

            self.assert_reference(second, 2)

        self.p.unchanged()

        result = self.p.send(
            self.p.authorized(policy=second)
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

    def test_03_competing_writers_share_one_monotonic_cas_backend(self):

        gateway_a = self.p.gateway
        gateway_b = self.p.make_gateway()

        request_a = self.p.authorized()

        request_b = self.p.authorized(
            writer_id="writer-beta",
            signer=self.p.f.bob,
            request=self.p.f.request(
                operation_id=remote.floor_contract.OP_B,
            ),
        )

        with ThreadPoolExecutor(max_workers=2) as pool:

            future_a = pool.submit(
                gateway_a.exchange,
                request_a,
            )

            future_b = pool.submit(
                gateway_b.exchange,
                request_b,
            )

            replies = (
                future_a.result(timeout=10),
                future_b.result(timeout=10),
            )

        results = [
            self.p.f.response(
                raw,
                operation="cas",
                challenge=b"c" * 32,
            )
            for raw in replies
        ]

        statuses = [
            result["status"]
            for result in results
        ]

        self.assertCountEqual(
            statuses,
            ["committed", "rejected"],
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

        self.assertEqual(
            self.p.f.fixture.fixture.read()["epoch"],
            2,
        )

    def test_04_concurrent_exact_replay_is_idempotent(self):

        request = self.p.authorized()

        gateways = [
            self.p.make_gateway()
            for _ in range(4)
        ]

        def exchange(gateway):

            return gateway.exchange(request)

        with ThreadPoolExecutor(max_workers=4) as pool:
            replies = list(
                pool.map(
                    exchange,
                    gateways,
                )
            )

        for raw in replies:

            result = self.p.f.response(
                raw,
                operation="cas",
                challenge=b"c" * 32,
            )

            self.assertEqual(
                (result["status"], result["epoch"]),
                ("committed", 2),
            )

        self.assertEqual(
            self.operation_count(),
            1,
        )

    def test_05_all_writers_revoked_preserves_public_read_and_lookup(self):

        second = self.p.next_policy(
            revoked=(
                "writer-alpha",
                "writer-beta",
            ),
        )

        self.p.publish(second)

        for writer_id, signer in (
            ("writer-alpha", self.p.f.alice),
            ("writer-beta", self.p.f.bob),
        ):

            with self.subTest(writer=writer_id):

                with self.assertRaises(ValueError):
                    self.p.gateway.exchange(
                        self.p.authorized(
                            policy=second,
                            writer_id=writer_id,
                            signer=signer,
                        )
                    )

        self.p.unchanged()

        self.assert_reference(second, 2)

        client = self.p.f.fixture.make_client(
            transport=self.p.gateway,
        )

        self.assertEqual(
            self.p.f.fixture.read(client)["epoch"],
            1,
        )

        self.assertEqual(
            self.public_lookup()["status"],
            "unknown",
        )

    def test_06_revoked_writer_tombstone_key_cannot_be_replaced(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.p.publish(second)

        changed = dict(
            self.p.f.writer_keys
        )

        changed["writer-alpha"] = policy.public_key(
            self.p.f.attacker
        )

        third = self.p.next_policy(
            second,
            writers=changed,
        )

        with self.assertRaises(ValueError):
            self.p.publish(third)

        self.assert_reference(second, 2)

        self.p.unchanged()

    def test_07_revoked_key_cannot_be_duplicated_under_new_identity(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.p.publish(second)

        changed = dict(
            self.p.f.writer_keys
        )

        changed["writer-charlie"] = policy.public_key(
            self.p.f.alice
        )

        third = self.p.next_policy(
            second,
            writers=changed,
        )

        with self.assertRaises(ValueError):
            self.p.publish(third)

        self.assert_reference(second, 2)

        self.p.unchanged()

    def test_08_reserved_signing_roles_cannot_be_enrolled_as_writers(self):

        reserved_keys = (
            self.p.root_key,
            policy.public_key(self.p.backend.signer),
            self.p.backend.authority_public_key,
            self.p.backend.witness_public_key,
        )

        for key in reserved_keys:

            with self.subTest(key=key.hex()):

                changed = dict(
                    self.p.f.writer_keys
                )

                changed["writer-charlie"] = key

                candidate = self.p.next_policy(
                    writers=changed,
                )

                with self.assertRaises(ValueError):
                    self.p.publish(candidate)

                self.assert_reference(
                    self.p.initial,
                    1,
                )

        self.p.unchanged()

    def test_09_invalid_signed_policy_pair_shapes_fail_closed(self):

        valid = self.p.next_policy()
        message, signature = valid

        damaged_signature = (
            bytes([signature[0] ^ 1])
            + signature[1:]
        )

        invalid = (
            None,
            message,
            (),
            (message,),
            list(valid),
            (bytearray(message), signature),
            (message, bytearray(signature)),
            (message, b""),
            (message, signature[:-1]),
            (message, damaged_signature),
            (message, signature, b"extra"),
        )

        for candidate in invalid:

            with self.subTest(
                candidate=repr(candidate)[:60],
            ):

                with self.assertRaises(ValueError):
                    self.p.publish(candidate)

                self.assert_reference(
                    self.p.initial,
                    1,
                )

        self.p.unchanged()

    def test_10_valid_signature_does_not_authorize_noncanonical_policy_json(self):

        message = self.p.next_policy()[0]

        duplicate = message.replace(
            b'"version":1',
            b'"version":1,"version":1',
            1,
        )

        self.assertNotEqual(
            duplicate,
            message,
        )

        invalid_documents = (
            message + b" ",
            duplicate,
            b"{}",
            b"[]",
            b"\xff",
        )

        for damaged in invalid_documents:

            with self.subTest(
                document=repr(damaged)[:60],
            ):

                signed = (
                    damaged,
                    self.p.root.sign(damaged),
                )

                with self.assertRaises(ValueError):
                    self.p.publish(signed)

        self.assert_reference(
            self.p.initial,
            1,
        )

        self.p.unchanged()

    def test_11_invalid_bootstrap_epoch_and_predecessor_pairs_rejected(self):

        invalid = (
            self.p.policy(epoch=0),
            self.p.policy(epoch=True),
            self.p.policy(epoch=-1),
            self.p.policy(epoch=1 << 63),
            self.p.policy(
                epoch=1,
                previous="ab" * 32,
            ),
            self.p.policy(
                epoch=2,
                previous="0" * 64,
            ),
        )

        for candidate in invalid:

            with self.subTest(
                candidate=policy.digest(candidate),
            ):

                with self.assertRaises(ValueError):
                    self.p.make_authority(candidate)

        self.assert_reference(
            self.p.initial,
            1,
        )

        self.p.unchanged()

    def test_12_multiple_rotations_require_latest_writer_key(self):

        original_gateway = self.p.gateway

        replacement = dict(
            self.p.f.writer_keys
        )

        replacement["writer-alpha"] = policy.public_key(
            self.p.f.attacker
        )

        second = self.p.next_policy(
            writers=replacement,
        )

        self.p.publish(second)

        latest_signer = Ed25519PrivateKey.generate()

        replacement["writer-alpha"] = policy.public_key(
            latest_signer
        )

        third = self.p.next_policy(
            second,
            writers=replacement,
        )

        self.p.publish(third)

        for signer in (
            self.p.f.alice,
            self.p.f.attacker,
        ):

            with self.assertRaises(ValueError):
                original_gateway.exchange(
                    self.p.authorized(
                        policy=third,
                        signer=signer,
                    )
                )

        for old_policy, old_signer in (
            (self.p.initial, self.p.f.alice),
            (second, self.p.f.attacker),
        ):

            with self.assertRaises(ValueError):
                original_gateway.exchange(
                    self.p.authorized(
                        policy=old_policy,
                        signer=old_signer,
                    )
                )

        self.p.unchanged()

        self.assert_reference(third, 3)

        result = self.p.send(
            self.p.authorized(
                policy=third,
                signer=latest_signer,
            ),
            gateway=original_gateway,
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

    def test_13_cas_envelope_mutations_invalidate_authorization(self):

        original = remote.parse_canonical(
            self.p.authorized()
        )

        inner = remote.parse_canonical(
            bytes.fromhex(
                original["request_hex"]
            )
        )

        altered_request = remote.canonical({
            **inner,
            "next_minimum_generation": 3,
        })

        mutations = (
            {"policy_id": "different-policy"},
            {"policy_epoch": 2},
            {"policy_epoch": True},
            {"policy_sha256": "ab" * 32},
            {"writer_id": "writer-beta"},
            {
                "request_hex":
                    altered_request.hex(),
            },
            {
                "writer_signature_hex":
                    "00" * 64,
            },
            {"extra": 1},
        )

        for changes in mutations:

            with self.subTest(changes=changes):

                damaged = remote.canonical({
                    **original,
                    **changes,
                })

                with self.assertRaises(ValueError):
                    self.p.gateway.exchange(damaged)

        self.p.unchanged()

    def test_14_valid_writer_signature_cannot_authorize_invalid_inner_cas(self):

        invalid = (
            self.p.f.request("read"),
            self.p.f.request("lookup"),
            self.p.f.request(
                floor_id="different-floor",
            ),
            self.p.f.request(
                subject_id="different-subject",
            ),
            self.p.f.request(
                challenge_hex="ff",
            ),
            self.p.f.request(
                expected_epoch=True,
            ),
            self.p.f.request(
                next_epoch=3,
            ),
            self.p.f.request(
                next_minimum_generation=0,
            ),
            self.p.f.request(
                extra=1,
            ),
            b'{"operation":"cas","operation":"read"}',
            self.p.f.request() + b" ",
            b"x" * 4097,
        )

        for request in invalid:

            with self.subTest(
                request=repr(request)[:60],
            ):

                with self.assertRaises(ValueError):
                    self.p.gateway.exchange(
                        self.p.authorized(
                            request=request,
                        )
                    )

        self.p.unchanged()

    def test_15_rejected_authorizations_never_invoke_sqlite_cas(self):

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.p.publish(second)

        requests = (
            self.p.f.request(),
            self.p.f.authorized(),
            self.p.authorized(),
            self.p.authorized(
                policy=second,
            ),
            self.p.authorized(
                policy=second,
                writer_id="writer-beta",
                signer=self.p.f.attacker,
            ),
            self.p.authorized(
                policy=second,
                writer_id="writer-charlie",
                signer=self.p.f.attacker,
            ),
        )

        backend_type = type(self.p.backend)

        with patch.object(
            backend_type,
            "advance_if_current",
            side_effect=AssertionError(
                "Unauthorized backend access"
            ),
        ) as backend_cas:

            for request in requests:

                with self.assertRaises(ValueError):
                    self.p.gateway.exchange(request)

            backend_cas.assert_not_called()

        self.p.unchanged()

    def test_16_rejected_policy_update_preserves_current_authorization_state(self):

        previous_reference = self.reference()

        invalid = self.p.policy(
            epoch=2,
            previous="ab" * 32,
            revoked=("writer-alpha",),
        )

        with self.assertRaises(ValueError):
            self.p.publish(invalid)

        self.assertEqual(
            self.reference(),
            previous_reference,
        )

        valid = self.p.next_policy()

        self.p.publish(valid)

        self.assert_reference(valid, 2)

        result = self.p.send(
            self.p.authorized(
                policy=valid,
            )
        )

        self.assertEqual(
            result["status"],
            "committed",
        )

    def test_17_precommit_cas_failure_releases_policy_lock(self):

        backend_type = type(self.p.backend)

        with patch.object(
            backend_type,
            "advance_if_current",
            side_effect=OSError(
                "Injected precommit failure"
            ),
        ):

            with self.assertRaises(ValueError):
                self.p.gateway.exchange(
                    self.p.authorized()
                )

        self.p.unchanged()

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.p.publish(second)

        self.assert_reference(second, 2)

        result = self.p.send(
            self.p.authorized(
                policy=second,
                writer_id="writer-beta",
                signer=self.p.f.bob,
            )
        )

        self.assertEqual(
            (result["status"], result["epoch"]),
            ("committed", 2),
        )

    def test_18_postcommit_reply_loss_and_revocation_preserve_lookup_recovery(self):

        backend_type = type(self.p.backend)

        original_cas = (
            backend_type.advance_if_current
        )

        request = self.p.authorized()

        def lose_reply(backend, **kwargs):

            original_cas(
                backend,
                **kwargs,
            )

            raise OSError(
                "Injected lost postcommit reply"
            )

        with patch.object(
            backend_type,
            "advance_if_current",
            lose_reply,
        ):

            with self.assertRaises(ValueError):
                self.p.gateway.exchange(request)

        self.assertEqual(
            self.operation_count(),
            1,
        )

        self.assertEqual(
            self.p.f.fixture.fixture.read()["epoch"],
            2,
        )

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.p.publish(second)

        with self.assertRaises(ValueError):
            self.p.gateway.exchange(request)

        result = self.public_lookup()

        self.assertEqual(
            result["status"],
            "committed",
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

    def test_19_legacy_v1_gateway_is_not_automatically_fenced_known_limit(self):

        legacy_gateway = self.p.f.adapter

        second = self.p.next_policy(
            revoked=("writer-alpha",),
        )

        self.p.publish(second)

        with self.assertRaises(ValueError):
            self.p.gateway.exchange(
                self.p.authorized(
                    policy=second,
                )
            )

        self.p.unchanged()

        # Explicit deployment limit:
        # A reachable legacy gateway is outside the new policy lock
        # and retains its original authorization snapshot.

        legacy_result = self.p.f.send(
            self.p.f.authorized(),
            adapter=legacy_gateway,
        )

        self.assertEqual(
            (
                legacy_result["status"],
                legacy_result["epoch"],
            ),
            ("committed", 2),
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )

        self.assert_reference(second, 2)

    def test_20_root_can_reenroll_previously_rotated_key_known_limit(self):

        original_key = policy.public_key(
            self.p.f.alice
        )

        replacement = dict(
            self.p.f.writer_keys
        )

        replacement["writer-alpha"] = policy.public_key(
            self.p.f.attacker
        )

        second = self.p.next_policy(
            writers=replacement,
        )

        self.p.publish(second)

        with self.assertRaises(ValueError):
            self.p.gateway.exchange(
                self.p.authorized(
                    policy=second,
                    signer=self.p.f.alice,
                )
            )

        self.p.unchanged()

        # Explicit known limit:
        # There is no permanent historical retirement catalog
        # for keys replaced by ordinary rotation.
        #
        # A trusted policy root may deliberately enroll an old
        # rotated key under another non-revoked identity.
        # This is not an unsigned policy update.

        replacement["writer-charlie"] = original_key

        third = self.p.next_policy(
            second,
            writers=replacement,
        )

        self.p.publish(third)

        self.assert_reference(third, 3)

        result = self.p.send(
            self.p.authorized(
                policy=third,
                writer_id="writer-charlie",
                signer=self.p.f.alice,
            )
        )

        self.assertEqual(
            (result["status"], result["epoch"]),
            ("committed", 2),
        )

        self.assertEqual(
            self.operation_count(),
            1,
        )


if __name__ == "__main__":
    unittest.main()
