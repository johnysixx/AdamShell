"""Adversarial protected writer policy authority tests.

Fault injection covers protected root transition boundaries,
policy recovery, authenticated observations and shared fencing.

The reference root remains an explicitly trusted, single-process
backend. Independent replacement is not prevented by static identity.
"""

import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from unittest.mock import patch

import test_a44_witness_deployment_floor_writer_policy_protected_root_authority_contract as contract


class A44ProtectedRootAuthorityAdversarialTests(unittest.TestCase):

    def setUp(self):

        self.f = contract.A44ProtectedRootAuthorityContractTests(
            "test_01_explicit_bootstrap_and_open"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.d = self.f.d
        self.p = self.f.p
        self.s = self.f.s

        self.root = self.f.root
        self.authority = self.f.authority
        self.genesis = self.f.genesis

    def test_01_root_prepare_failure_prevents_policy_mutation(self):

        second = self.f.candidate()
        initial = self.root.read()

        original = type(self.root).compare_and_set
        reached = []

        def fail_prepare(instance, *, expected, replacement):

            if replacement.durable_state.prepared is not None:

                reached.append(replacement)

                raise OSError("Root prepare failed before commit")

            return original(
                instance,
                expected=expected,
                replacement=replacement,
            )

        with patch.object(
            type(self.root),
            "compare_and_set",
            fail_prepare,
        ):

            with self.assertRaises(ValueError):
                self.f.publish(second)

        self.assertEqual(len(reached), 1)

        self.assertEqual(
            reached[0].durable_state.prepared.signed_policy,
            second,
        )

        self.assertEqual(self.root.read(), initial)

        self.s.assert_history(self.genesis)
        self.d.assert_floor(1, 0)

        self.assertEqual(
            self.f.publish(second),
            self.d.pair(second, 2),
        )

        self.f.stable(second, 2, 3)

    def test_02_prepare_ack_loss_retains_candidate_before_policy_commit(self):

        second = self.f.candidate()

        original = type(self.root).compare_and_set
        reached = []

        def lose_ack(instance, *, expected, replacement):

            result = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            if replacement.durable_state.prepared is not None:

                reached.append(result)

                raise OSError("Root prepare acknowledgement lost")

            return result

        with patch.object(
            type(self.root),
            "compare_and_set",
            lose_ack,
        ):

            with self.assertRaises(ValueError):
                self.f.publish(second)

        self.assertEqual(len(reached), 1)

        retained = self.f.pending(second)

        self.assertEqual(
            reached[0],
            retained.reference(),
        )

        self.s.assert_history(self.genesis)

        fresh = self.f.reopen()

        self.assertEqual(fresh.root_state(), retained)

        self.f.blocked(
            gateway=self.f.make_gateway(fresh),
        )

        self.assertEqual(
            fresh.recover_publication(),
            self.d.pair(second, 2),
        )

        self.f.stable(second, 2, 3)

        self.s.assert_history(self.genesis, second)
        self.d.assert_floor(1, 0)

    def test_03_incorrect_root_receipt_prevents_floor_mutation(self):

        initial = self.root.read()

        second = self.p.next_policy()

        self.d.h.publish_external(second)

        original = type(self.root).compare_and_set
        reached = []

        def wrong_receipt(instance, *, expected, replacement):

            actual = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            reached.append(actual)

            return initial.reference()

        with patch.object(
            type(self.root),
            "compare_and_set",
            wrong_receipt,
        ):

            self.f.blocked(signed_policy=second)

        self.assertEqual(len(reached), 1)

        observed = self.f.stable(second, 2, 2)

        self.assertEqual(
            reached[0],
            observed.reference(),
        )

        self.d.assert_floor(1, 0)

        self.d.assert_committed(
            self.f.send(second),
            2,
        )

        self.assertEqual(self.root.read(), observed)

        self.d.assert_floor(2, 1)

    def test_04_observation_ack_loss_survives_policy_rollback(self):

        old = self.d.snapshot()

        second = self.p.next_policy()

        self.d.h.publish_external(second)

        original = type(self.root).compare_and_set
        reached = []

        def lose_ack(instance, *, expected, replacement):

            result = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            reached.append(result)

            raise OSError("Protected observation acknowledgement lost")

        with patch.object(
            type(self.root),
            "compare_and_set",
            lose_ack,
        ):

            self.f.blocked(signed_policy=second)

        self.assertEqual(len(reached), 1)

        retained = self.f.stable(second, 2, 2)

        self.d.assert_floor(1, 0)

        self.d.restore(old)

        with self.assertRaises(ValueError):
            self.f.reopen()

        self.f.blocked()

        self.assertEqual(self.root.read(), retained)

        self.d.assert_floor(1, 0)

    def test_05_root_unavailable_blocks_cas_but_not_public_recovery(self):

        self.d.assert_committed(
            self.f.send(),
            2,
        )

        retained = self.root.read()

        with patch.object(
            type(self.root),
            "read",
            side_effect=OSError("Protected root unavailable"),
        ):

            with self.assertRaises(ValueError):
                self.f.reopen()

            with self.assertRaises(ValueError):
                self.authority.current_policy_reference()

            with self.assertRaises(ValueError):
                self.authority.recover_publication()

            self.f.blocked(
                request=self.p.next_cas(),
            )

            self.assertEqual(
                self.d.public_read(self.f.gateway)["epoch"],
                2,
            )

            self.assertEqual(
                self.d.public_lookup(self.f.gateway)["status"],
                "committed",
            )

        self.assertEqual(self.root.read(), retained)

        self.d.assert_floor(2, 1)

    def test_06_recovery_finalizes_candidate_before_observing_descendant(self):

        second = self.f.candidate()

        self.f.fail_publication(
            second,
            after_commit=True,
        )

        self.s.assert_history(self.genesis, second)

        third = self.p.next_policy(
            previous=second,
        )

        self.d.h.publish_external(third)

        retained = self.f.pending(second)

        original = type(self.root).compare_and_set
        transitions = []

        def record_transition(instance, *, expected, replacement):

            result = original(
                instance,
                expected=expected,
                replacement=replacement,
            )

            transitions.append(replacement)

            return result

        with patch.object(
            type(self.root),
            "compare_and_set",
            record_transition,
        ):

            self.assertEqual(
                self.authority.recover_publication(),
                self.d.pair(third, 3),
            )

        self.assertEqual(
            [state.revision for state in transitions],
            [3, 4],
        )

        self.assertEqual(
            transitions[0].durable_state.anchor,
            self.d.ref(second, 2),
        )

        self.assertEqual(
            transitions[1].durable_state.anchor,
            self.d.ref(third, 3),
        )

        self.assertTrue(
            all(
                state.durable_state.prepared is None
                for state in transitions
            )
        )

        self.assertIsNotNone(
            retained.durable_state.prepared
        )

        final = self.f.stable(third, 3, 4)

        self.assertEqual(
            self.authority.recover_publication(),
            self.d.pair(third, 3),
        )

        self.assertEqual(self.root.read(), final)

        self.s.assert_history(
            self.genesis,
            second,
            third,
        )

        self.f.blocked(signed_policy=third)
        self.d.assert_floor(1, 0)

    def test_07_repeated_recovery_failure_preserves_prepared(self):

        second = self.f.candidate()

        retained = self.f.fail_publication(
            second,
            after_commit=False,
        )

        with patch.object(
            self.f.m.durable,
            "_append_policy",
            side_effect=OSError("Recovery append unavailable"),
        ) as append:

            for attempt in range(2):

                with self.assertRaises(ValueError):
                    self.authority.recover_publication()

                self.assertEqual(
                    self.root.read(),
                    retained,
                )

                self.s.assert_history(self.genesis)

                self.f.blocked()

            self.assertEqual(append.call_count, 2)

        self.assertEqual(
            self.authority.recover_publication(),
            self.d.pair(second, 2),
        )

        self.f.stable(second, 2, 3)

        self.s.assert_history(self.genesis, second)
        self.d.assert_floor(1, 0)

    def test_08_structural_prepared_state_requires_valid_signature(self):

        second = self.f.candidate()

        invalid_signature = (
            second[0],
            b"\x00" * 64,
        )

        initial = self.root.read()

        prepared = self.d.prepared_type(
            predecessor=initial.durable_state.anchor,
            candidate=self.d.ref(second, 2),
            signed_policy=invalid_signature,
        )

        invalid = replace(
            initial,
            revision=2,
            durable_state=self.d.state_type(
                anchor=initial.durable_state.anchor,
                prepared=prepared,
            ),
        )

        # The backend checks structural transitions.
        # The authority must authenticate the policy signature.

        self.root.compare_and_set(
            expected=initial.reference(),
            replacement=invalid,
        )

        with self.assertRaises(ValueError):
            self.f.reopen()

        with self.assertRaises(ValueError):
            self.authority.root_state()

        with self.assertRaises(ValueError):
            self.authority.recover_publication()

        self.f.blocked()

        self.assertEqual(self.root.read(), invalid)

        self.s.assert_history(self.genesis)
        self.d.assert_floor(1, 0)

    def test_09_invalid_publication_retains_authenticated_observation(self):

        second = self.f.candidate()

        self.d.h.publish_external(second)

        third = self.p.next_policy(
            previous=second,
        )

        invalid = (
            third[0],
            b"\x00" * 64,
        )

        with self.assertRaises(ValueError):
            self.f.publish(invalid)

        observed = self.f.stable(second, 2, 2)

        self.s.assert_history(self.genesis, second)

        self.f.blocked(signed_policy=second)

        self.assertEqual(self.root.read(), observed)

        self.assertEqual(
            self.f.publish(third),
            self.d.pair(third, 3),
        )

        self.f.stable(third, 3, 4)

        self.s.assert_history(
            self.genesis,
            second,
            third,
        )

        self.d.assert_floor(1, 0)

    def test_10_competing_publications_have_exactly_one_winner(self):

        peer = self.f.reopen()

        first_policy = self.f.candidate()

        second_policy = self.p.next_policy(
            revoked=("writer-beta",),
        )

        self.assertNotEqual(
            self.d.pair(first_policy, 2),
            self.d.pair(second_policy, 2),
        )

        barrier = threading.Barrier(2)

        def publish(authority, policy):

            barrier.wait(timeout=10)

            try:

                result = self.f.publish(
                    policy,
                    authority=authority,
                )

                return ("committed", policy, result)

            except ValueError:

                return ("rejected", policy, None)

        with ThreadPoolExecutor(max_workers=2) as pool:

            first = pool.submit(
                publish,
                self.authority,
                first_policy,
            )

            second = pool.submit(
                publish,
                peer,
                second_policy,
            )

            results = [
                first.result(timeout=30),
                second.result(timeout=30),
            ]

        self.assertCountEqual(
            [entry[0] for entry in results],
            ["committed", "rejected"],
        )

        winner = next(
            entry for entry in results
            if entry[0] == "committed"
        )

        winning_policy = winner[1]

        self.assertEqual(
            winner[2],
            self.d.pair(winning_policy, 2),
        )

        retained = self.f.stable(
            winning_policy,
            2,
            3,
        )

        self.assertEqual(
            peer.root_state(),
            retained,
        )

        self.s.assert_history(
            self.genesis,
            winning_policy,
        )

        self.d.assert_floor(1, 0)

    def test_11_concurrent_recovery_is_idempotent(self):

        second = self.f.candidate()

        self.f.fail_publication(
            second,
            after_commit=False,
        )

        peer = self.f.reopen()

        barrier = threading.Barrier(2)

        def recover(authority):

            barrier.wait(timeout=10)

            return authority.recover_publication()

        with ThreadPoolExecutor(max_workers=2) as pool:

            first = pool.submit(
                recover,
                self.authority,
            )

            second_recovery = pool.submit(
                recover,
                peer,
            )

            expected = self.d.pair(second, 2)

            self.assertEqual(
                first.result(timeout=30),
                expected,
            )

            self.assertEqual(
                second_recovery.result(timeout=30),
                expected,
            )

        retained = self.f.stable(second, 2, 3)

        self.assertEqual(
            peer.root_state(),
            retained,
        )

        self.s.assert_history(self.genesis, second)

        self.f.blocked(signed_policy=second)

        self.d.assert_floor(1, 0)

    def test_12_same_identity_independent_root_is_explicit_trust_boundary(self):

        old = self.d.snapshot(
            "independent-protected-root-policy.sqlite3"
        )

        second = self.f.candidate()

        self.f.publish(second)

        retained = self.f.stable(second, 2, 3)

        self.f.blocked(signed_policy=second)

        replacement_root = self.f.new_root()

        # This intentionally violates the single independently
        # trusted root assumption. Static identity does not prove
        # that a replacement backend retains previous state.

        replacement = self.f.bootstrap(
            path=old,
            root_backend=replacement_root,
        )

        self.assertEqual(
            replacement.root_state().identity,
            retained.identity,
        )

        self.assertEqual(
            replacement.current_policy_reference(),
            self.d.pair(self.genesis, 1),
        )

        self.assertEqual(
            replacement.root_state().revision,
            1,
        )

        self.d.assert_committed(
            self.f.send(
                self.genesis,
                gateway=self.f.make_gateway(replacement),
            ),
            2,
        )

        self.assertEqual(self.root.read(), retained)

        self.f.blocked(
            signed_policy=second,
            request=self.p.next_cas(),
        )

        self.d.assert_floor(2, 1)


if __name__ == "__main__":
    unittest.main()
