"""Adversarial contract for the reference protected root.

The in-memory root models independent trusted state.
Independent replacement roots are an explicit trust boundary.
"""

import copy
import hashlib
import pickle
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import test_a44_witness_deployment_floor_writer_policy_protected_root_backend_contract as contract


class A44ProtectedRootBackendAdversarialTests(unittest.TestCase):

    def setUp(self):

        self.f = contract.A44ProtectedRootBackendContractTests(
            "test_01_explicit_provisioning"
        )

        self.addCleanup(self.f.doCleanups)
        self.f.setUp()

        self.m = self.f.m
        self.d = self.f.d

        self.backend = self.f.backend
        self.identity = self.f.identity
        self.initial = self.f.initial

    def provision(self):
        self.f.provision()

    def pending(self):
        return self.f.pending()

    def advance(self, old, new):
        return self.f.advance(old, new)

    def descendant(self, state, epoch, digest):

        return replace(
            state,
            revision=state.revision + 1,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=self.d.PolicyReference(
                    epoch=epoch,
                    sha256=digest,
                ),
            ),
        )

    def test_01_backend_copy_and_serialization_rejected(self):

        self.provision()

        before = self.backend.read()

        for operation in (
            copy.copy,
            copy.deepcopy,
            pickle.dumps,
        ):

            with self.assertRaises(TypeError):
                operation(self.backend)

        self.assertEqual(self.backend.read(), before)

        self.advance(before, self.pending())

    def test_02_backend_reinitialization_cannot_erase_state(self):

        self.provision()

        pending = self.pending()
        self.advance(self.initial, pending)

        with self.assertRaises(ValueError):

            self.backend.__init__(
                identity=self.identity,
            )

        with self.assertRaises(ValueError):

            self.backend.__init__(
                identity=replace(
                    self.identity,
                    provisioning_nonce=b"x" * 32,
                ),
            )

        self.assertEqual(self.backend.read(), pending)

        self.advance(
            pending,
            self.f.finalized(pending),
        )

    def test_03_no_op_transition_cannot_consume_revision(self):

        self.provision()

        invalid = replace(
            self.initial,
            revision=2,
        )

        with self.assertRaises(ValueError):
            self.advance(self.initial, invalid)

        self.assertEqual(self.backend.read(), self.initial)

        pending = self.pending()

        self.advance(self.initial, pending)

        self.assertEqual(self.backend.read(), pending)
        self.assertEqual(pending.revision, 2)

    def test_04_noncanonical_transition_arguments_rejected(self):

        self.provision()

        pending = self.pending()

        with self.assertRaises(ValueError):

            self.backend.compare_and_set(
                expected={
                    "revision": 1,
                    "sha256": self.initial.reference().sha256,
                },
                replacement=pending,
            )

        with self.assertRaises(ValueError):

            self.backend.compare_and_set(
                expected=self.initial.reference(),
                replacement={},
            )

        self.assertEqual(self.backend.read(), self.initial)

        self.advance(self.initial, pending)

    def test_05_every_identity_component_is_immutable(self):

        self.provision()

        pending = self.pending()

        identities = (
            replace(
                self.identity,
                deployment_id="different-deployment",
            ),
            replace(
                self.identity,
                configuration_sha256="ef" * 32,
            ),
            replace(
                self.identity,
                provisioning_nonce=b"x" * 32,
            ),
        )

        for identity in identities:

            replacement = replace(
                pending,
                identity=identity,
            )

            with self.assertRaises(ValueError):

                self.advance(
                    self.initial,
                    replacement,
                )

            self.assertEqual(
                self.backend.read(),
                self.initial,
            )

        self.advance(self.initial, pending)

    def test_06_pending_cannot_finalize_directly_to_descendant(self):

        self.provision()

        pending = self.pending()
        self.advance(self.initial, pending)

        invalid = self.descendant(
            pending,
            3,
            "12" * 32,
        )

        with self.assertRaises(ValueError):
            self.advance(pending, invalid)

        self.assertEqual(self.backend.read(), pending)

        finalized = self.f.finalized(pending)

        self.advance(pending, finalized)

        descendant = self.descendant(
            finalized,
            3,
            "12" * 32,
        )

        self.advance(finalized, descendant)

        self.assertEqual(
            self.backend.read(),
            descendant,
        )

        self.assertEqual(descendant.revision, 4)

    def test_07_preparation_cannot_skip_current_anchor(self):

        self.provision()

        shifted_anchor = self.d.PolicyReference(
            epoch=2,
            sha256="ef" * 32,
        )

        message = b"candidate-after-skipped-anchor"

        prepared = self.d.PreparedPolicyPublication(
            predecessor=shifted_anchor,
            candidate=self.d.PolicyReference(
                epoch=3,
                sha256=hashlib.sha256(message).hexdigest(),
            ),
            signed_policy=(message, b"s" * 64),
        )

        invalid = replace(
            self.initial,
            revision=2,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=shifted_anchor,
                prepared=prepared,
            ),
        )

        with self.assertRaises(ValueError):

            self.advance(
                self.initial,
                invalid,
            )

        self.assertEqual(self.backend.read(), self.initial)

        self.advance(self.initial, self.pending())

    def test_08_concurrent_provisioning_has_exactly_one_winner(self):

        barrier = threading.Barrier(2)

        def provision():

            barrier.wait(timeout=10)

            try:

                result = self.backend.provision(
                    state=self.initial,
                )

                return ("committed", result)

            except ValueError:

                return ("rejected", None)

        with ThreadPoolExecutor(max_workers=2) as pool:

            first = pool.submit(provision)
            second = pool.submit(provision)

            results = [
                first.result(timeout=15),
                second.result(timeout=15),
            ]

        self.assertCountEqual(
            results,
            [
                ("committed", self.initial.reference()),
                ("rejected", None),
            ],
        )

        self.assertEqual(self.backend.read(), self.initial)

    def test_09_conflicting_preparations_have_exactly_one_winner(self):

        self.provision()

        first_state = self.f.pending(
            self.f.prepared(message=b"candidate-first")
        )

        second_state = self.f.pending(
            self.f.prepared(message=b"candidate-second")
        )

        barrier = threading.Barrier(2)

        def attempt(candidate):

            barrier.wait(timeout=10)

            try:

                result = self.advance(
                    self.initial,
                    candidate,
                )

                return ("committed", result)

            except ValueError:

                return ("rejected", None)

        with ThreadPoolExecutor(max_workers=2) as pool:

            first = pool.submit(attempt, first_state)
            second = pool.submit(attempt, second_state)

            results = [
                first.result(timeout=15),
                second.result(timeout=15),
            ]

        self.assertCountEqual(
            [status for status, value in results],
            ["committed", "rejected"],
        )

        retained = self.backend.read()

        self.assertIn(
            retained,
            (first_state, second_state),
        )

        self.assertIn(
            ("committed", retained.reference()),
            results,
        )

        self.assertEqual(retained.revision, 2)

        self.advance(
            retained,
            self.f.finalized(retained),
        )

        self.assertEqual(
            self.backend.read().revision,
            3,
        )

    def test_10_committed_transition_survives_enclosing_exception(self):

        self.provision()

        pending = self.pending()

        with self.assertRaises(OSError):

            with self.backend.exclusive():

                with self.backend.exclusive():

                    self.advance(
                        self.initial,
                        pending,
                    )

                raise OSError("Publication interrupted")

        self.assertEqual(self.backend.read(), pending)

        finalized = self.f.finalized(pending)

        with self.assertRaises(OSError):

            with self.backend.exclusive():

                self.advance(
                    pending,
                    finalized,
                )

                raise OSError("Finalization acknowledgement lost")

        self.assertEqual(self.backend.read(), finalized)

    def test_11_old_references_cannot_authorize_later_revision(self):

        self.provision()

        pending = self.pending()
        finalized = self.f.finalized(pending)

        self.advance(self.initial, pending)
        self.advance(pending, finalized)

        descendant = self.descendant(
            finalized,
            3,
            "12" * 32,
        )

        for stale in (self.initial, pending):

            with self.assertRaises(ValueError):

                self.backend.compare_and_set(
                    expected=stale.reference(),
                    replacement=descendant,
                )

            self.assertEqual(
                self.backend.read(),
                finalized,
            )

        self.advance(finalized, descendant)

        self.assertEqual(self.backend.read(), descendant)

    def test_12_independent_root_replacement_is_explicit_trust_boundary(self):

        self.provision()

        pending = self.pending()
        finalized = self.f.finalized(pending)

        self.advance(self.initial, pending)
        self.advance(pending, finalized)

        replacement = self.m.InMemoryProtectedRootBackend(
            identity=self.identity,
        )

        # Deliberately construct an independent trusted root.
        # Static identity alone does not provide global uniqueness
        # or persistence across replacement of the trusted backend.

        replacement.provision(state=self.initial)

        self.assertEqual(
            replacement.identity,
            self.backend.identity,
        )

        self.assertEqual(
            replacement.read(),
            self.initial,
        )

        self.assertEqual(
            self.backend.read(),
            finalized,
        )

        self.assertNotEqual(
            replacement.read().reference(),
            self.backend.read().reference(),
        )


if __name__ == "__main__":
    unittest.main()
