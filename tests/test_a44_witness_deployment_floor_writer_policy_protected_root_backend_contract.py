"""Protected root backend contract.

The reference backend models a trusted independent root.
It is not itself hardware-backed or process-durable.

The backend protects canonical state transitions and serializes
cooperating callers. The authority must separately authenticate
policy signatures, history and writer authorization.
"""

import hashlib
import importlib
import json
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root"
)

DURABLE_MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_durable_high_water"
)


class A44ProtectedRootBackendContractTests(unittest.TestCase):

    def setUp(self):
        self.m = importlib.import_module(MODULE)
        self.d = importlib.import_module(DURABLE_MODULE)

        self.identity = self.m.ProtectedDeploymentIdentity(
            deployment_id="a44-protected-root",
            configuration_sha256="ab" * 32,
            provisioning_nonce=b"n" * 32,
        )

        self.anchor = self.d.PolicyReference(
            epoch=1,
            sha256="cd" * 32,
        )

        self.initial = self.m.ProtectedDurableRootState(
            identity=self.identity,
            revision=1,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=self.anchor,
            ),
        )

        self.backend = self.m.InMemoryProtectedRootBackend(
            identity=self.identity,
        )

    def provision(self):
        self.assertEqual(
            self.backend.provision(state=self.initial),
            self.initial.reference(),
        )
        self.assertEqual(self.backend.read(), self.initial)

    def prepared(self, message=b"candidate-A", signature=b"s" * 64):
        candidate = self.d.PolicyReference(
            epoch=2,
            sha256=hashlib.sha256(message).hexdigest(),
        )
        return self.d.PreparedPolicyPublication(
            predecessor=self.anchor,
            candidate=candidate,
            signed_policy=(message, signature),
        )

    def pending(self, prepared=None):
        if prepared is None:
            prepared = self.prepared()

        return replace(
            self.initial,
            revision=2,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=self.anchor,
                prepared=prepared,
            ),
        )

    def finalized(self, pending):
        return replace(
            pending,
            revision=3,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=pending.durable_state.prepared.candidate,
            ),
        )

    def advance(self, expected, replacement):
        return self.backend.compare_and_set(
            expected=expected.reference(),
            replacement=replacement,
        )

    def expected_digest(self, state):
        identity = state.identity
        durable = state.durable_state
        prepared = durable.prepared

        if prepared is None:
            pending = None
        else:
            pending = [
                prepared.predecessor.epoch,
                prepared.predecessor.sha256,
                prepared.candidate.epoch,
                prepared.candidate.sha256,
                prepared.signed_policy[0].hex(),
                prepared.signed_policy[1].hex(),
            ]

        payload = [
            "a44-protected-durable-root-state-v1",
            identity.deployment_id,
            identity.configuration_sha256,
            identity.provisioning_nonce.hex(),
            state.revision,
            durable.anchor.epoch,
            durable.anchor.sha256,
            pending,
        ]

        return hashlib.sha256(
            json.dumps(
                payload,
                ensure_ascii=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

    def test_01_explicit_provisioning(self):
        self.assertIsInstance(
            self.backend, self.m.ProtectedRootBackend
        )

        with self.assertRaises(ValueError):
            self.backend.read()

        with self.assertRaises(ValueError):
            self.advance(self.initial, self.pending())

        self.provision()

        with self.assertRaises(ValueError):
            self.backend.provision(state=self.initial)

        self.assertEqual(self.backend.read(), self.initial)

    def test_02_canonical_immutable_objects(self):
        self.provision()
        state = self.backend.read()
        reference = state.reference()

        self.assertIs(type(reference), self.m.ProtectedRootReference)

        with self.assertRaises(AttributeError):
            state.revision = 5

        with self.assertRaises(AttributeError):
            state.identity.provisioning_nonce = b"x" * 32

        with self.assertRaises(AttributeError):
            reference.revision = 5

        with self.assertRaises(AttributeError):
            state.durable_state.anchor.epoch = 5

        self.assertEqual(self.backend.read(), self.initial)

    def test_03_reference_commits_full_canonical_state(self):
        pending = self.pending()

        for state in (self.initial, pending, self.finalized(pending)):
            reference = state.reference()
            self.assertEqual(reference.revision, state.revision)
            self.assertEqual(reference.sha256, self.expected_digest(state))

        self.assertNotEqual(
            self.initial.reference().sha256,
            pending.reference().sha256,
        )

        self.assertEqual(
            self.initial.durable_state.anchor,
            pending.durable_state.anchor,
        )

    def test_04_reference_binds_identity_and_exact_signed_candidate(self):
        pending = self.pending()
        different_signature = self.pending(
            self.prepared(signature=b"t" * 64)
        )
        different_message = self.pending(
            self.prepared(message=b"candidate-B")
        )
        different_identity = replace(
            pending,
            identity=replace(
                self.identity,
                provisioning_nonce=b"x" * 32,
            ),
        )

        references = {
            state.reference().sha256
            for state in (
                pending,
                different_signature,
                different_message,
                different_identity,
            )
        }

        self.assertEqual(len(references), 4)

    def test_05_invalid_canonical_objects_rejected(self):
        for revision in (0, -1, True, "1"):
            with self.assertRaises(ValueError):
                replace(self.initial, revision=revision)

        with self.assertRaises(ValueError):
            replace(self.identity, provisioning_nonce=b"short")

        with self.assertRaises(ValueError):
            replace(self.identity, configuration_sha256="invalid")

        with self.assertRaises(ValueError):
            replace(self.initial, durable_state={})

        with self.assertRaises(ValueError):
            self.m.ProtectedRootReference(
                revision=True,
                sha256="ab" * 32,
            )

    def test_06_provisioning_identity_must_match(self):
        wrong = replace(
            self.initial,
            identity=replace(
                self.identity,
                provisioning_nonce=b"x" * 32,
            ),
        )

        with self.assertRaises(ValueError):
            self.backend.provision(state=wrong)

        with self.assertRaises(ValueError):
            self.backend.provision(state=self.pending())

        with self.assertRaises(ValueError):
            self.backend.provision(
                state=replace(self.initial, revision=2)
            )

        with self.assertRaises(ValueError):
            self.backend.read()

        self.provision()

    def test_07_prepare_then_finalize(self):
        self.provision()

        pending = self.pending()
        finalized = self.finalized(pending)

        self.assertEqual(
            self.advance(self.initial, pending),
            pending.reference(),
        )
        self.assertEqual(self.backend.read(), pending)

        self.assertEqual(
            self.advance(pending, finalized),
            finalized.reference(),
        )
        self.assertEqual(self.backend.read(), finalized)

        self.assertIsNone(self.initial.durable_state.prepared)
        self.assertIsNotNone(pending.durable_state.prepared)

    def test_08_stale_or_conflicting_expected_reference_rejected(self):
        self.provision()

        pending = self.pending()
        self.advance(self.initial, pending)

        with self.assertRaises(ValueError):
            self.advance(self.initial, self.pending(self.prepared(b"B")))

        with self.assertRaises(ValueError):
            self.backend.compare_and_set(
                expected=self.m.ProtectedRootReference(
                    revision=2,
                    sha256="ab" * 32,
                ),
                replacement=self.finalized(pending),
            )

        self.assertEqual(self.backend.read(), pending)

    def test_09_revision_and_identity_cannot_change_arbitrarily(self):
        self.provision()
        pending = self.pending()

        for invalid in (
            replace(pending, revision=1),
            replace(pending, revision=3),
            replace(
                pending,
                identity=replace(
                    self.identity,
                    provisioning_nonce=b"x" * 32,
                ),
            ),
        ):
            with self.assertRaises(ValueError):
                self.advance(self.initial, invalid)

        self.assertEqual(self.backend.read(), self.initial)

    def test_10_prepared_publication_cannot_abort_or_switch(self):
        self.provision()
        pending = self.pending()
        self.advance(self.initial, pending)

        aborted = replace(self.initial, revision=3)

        switched = replace(
            self.pending(self.prepared(b"alternative")),
            revision=3,
        )

        wrong_finalization = self.finalized(switched)

        wrong_finalization = replace(
            wrong_finalization,
            revision=3,
        )

        for invalid in (aborted, switched, wrong_finalization):
            with self.assertRaises(ValueError):
                self.advance(pending, invalid)

        self.assertEqual(self.backend.read(), pending)

        self.advance(pending, self.finalized(pending))

    def test_11_stable_anchor_cannot_rollback_or_fork(self):
        self.provision()
        pending = self.pending()
        self.advance(self.initial, pending)

        final = self.finalized(pending)
        self.advance(pending, final)

        rollback = replace(self.initial, revision=4)

        fork = replace(
            final,
            revision=4,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=self.d.PolicyReference(
                    epoch=2,
                    sha256="ef" * 32,
                ),
            ),
        )

        for invalid in (rollback, fork):
            with self.assertRaises(ValueError):
                self.advance(final, invalid)

        descendant = replace(
            final,
            revision=4,
            durable_state=self.d.DurablePolicyHighWaterState(
                anchor=self.d.PolicyReference(
                    epoch=3,
                    sha256="12" * 32,
                ),
            ),
        )

        # Signature and lineage verification is the authority's duty.
        self.advance(final, descendant)
        self.assertEqual(self.backend.read(), descendant)

    def test_12_shared_exclusive_fence_serializes_transition(self):
        self.provision()

        pending = self.pending()
        started = threading.Event()
        finished = threading.Event()

        def competitor():
            started.set()
            try:
                return self.advance(self.initial, pending)
            finally:
                finished.set()

        with ThreadPoolExecutor(max_workers=1) as pool:
            with self.backend.exclusive():
                future = pool.submit(competitor)
                self.assertTrue(started.wait(timeout=5))
                self.assertFalse(finished.wait(timeout=0.25))
                self.assertEqual(self.backend.read(), self.initial)

            self.assertEqual(
                future.result(timeout=10),
                pending.reference(),
            )

        self.assertEqual(self.backend.read(), pending)


if __name__ == "__main__":
    unittest.main()
