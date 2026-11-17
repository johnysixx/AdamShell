"""A44 independent-authority message contract.

These are structural and fail-closed protocol tests.
TestOnlyVerifier does NOT provide real authentication.

A production implementation must use a separately trusted
authority and independently provisioned verification keys
or authenticated transport. A caller-supplied verifier is
not, by itself, a trust root.

This module does not authorize receipt execution.
"""

import dataclasses
import importlib
import unittest

from core.existence.history_receipt_trust_floor import (
    _catalog_fingerprints,
)
from test_a44_current_trust_enforcement import lifecycle_pair


AUTHORITY = "adam-shell-provider-receipt-authority"
OPERATION = "rotate-provider-key-revision-2"


def api():
    return importlib.import_module(
        "core.existence."
        "history_receipt_trust_independent_authority_contract"
    )


def snapshot(lifecycle):
    return (
        lifecycle.revision,
        *_catalog_fingerprints(lifecycle),
    )


def make_intent(module):
    initial, revoked = lifecycle_pair()

    return module.AuthorityPublicationIntent(
        authority_id=AUTHORITY,
        operation_id=OPERATION,
        expected_committed=snapshot(initial),
        target=snapshot(revoked),
        expected_generation=7,
        fence_token=101,
    )


def make_reply(module, intent, *, prepared=False):
    status = (
        module.AuthorityReplyStatus.PREPARED
        if prepared
        else module.AuthorityReplyStatus.COMMITTED
    )

    return module.AuthorityAttestedReply(
        authority_id=intent.authority_id,
        operation_id=intent.operation_id,
        expected_committed=intent.expected_committed,
        target=intent.target,
        committed=(
            intent.expected_committed
            if prepared
            else intent.target
        ),
        pending_operation_id=(
            intent.operation_id if prepared else None
        ),
        status=status,
        generation=(8 if prepared else 9),
        fence_token=intent.fence_token,
        evidence=b"test-only-opaque-evidence",
    )


class TestOnlyVerifier:
    """A test stub; NOT cryptographic verification."""

    __test__ = False

    def __init__(self, answer=True):
        self.answer = answer
        self.calls = []

    def verify_attestation(self, reply):
        self.calls.append(reply)
        return self.answer


def assess(
    module,
    intent,
    reply,
    verifier,
    *,
    minimum_generation=7,
    minimum_fence_token=101,
):
    return module.require_attested_publication_reply(
        intent,
        reply,
        verifier=verifier,
        minimum_generation=minimum_generation,
        minimum_fence_token=minimum_fence_token,
    )


class A44IndependentAuthorityContractTests(unittest.TestCase):

    def test_intent_is_frozen_and_binds_catalog_snapshots(self):
        module = api()
        intent = make_intent(module)

        self.assertTrue(dataclasses.is_dataclass(intent))
        self.assertEqual(intent.authority_id, AUTHORITY)
        self.assertEqual(intent.operation_id, OPERATION)
        self.assertEqual(intent.expected_generation, 7)
        self.assertEqual(intent.fence_token, 101)
        self.assertEqual(intent.expected_committed[0], 1)
        self.assertEqual(intent.target[0], 2)

        with self.assertRaises(
            (dataclasses.FrozenInstanceError, AttributeError)
        ):
            intent.operation_id = "changed"

    def test_invalid_intent_is_rejected(self):
        module = api()
        intent = make_intent(module)

        bad_changes = (
            {"authority_id": ""},
            {"authority_id": " padded "},
            {"operation_id": ""},
            {"operation_id": " other "},
            {"expected_committed": intent.target},
            {"target": intent.expected_committed},
            {"target": list(intent.target)},
            {
                "target": (
                    intent.target[0],
                    "0" * 64,
                    intent.target[2],
                )
            },
            {"expected_generation": True},
            {"expected_generation": -1},
            {"fence_token": 0},
            {"fence_token": True},
        )

        for changes in bad_changes:
            with self.subTest(changes=repr(changes)):
                with self.assertRaises(ValueError):
                    dataclasses.replace(intent, **changes)

    def test_prepared_reply_requires_verified_evidence(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent, prepared=True)
        verifier = TestOnlyVerifier()

        result = assess(module, intent, reply, verifier)

        self.assertEqual(
            result,
            module.AuthorityReplyStatus.PREPARED,
        )
        self.assertEqual(verifier.calls, [reply])

    def test_committed_reply_recovers_lost_acknowledgement(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)
        verifier = TestOnlyVerifier()

        result = assess(
            module,
            intent,
            reply,
            verifier,
            minimum_generation=8,
        )

        self.assertEqual(
            result,
            module.AuthorityReplyStatus.COMMITTED,
        )
        self.assertEqual(reply.operation_id, OPERATION)
        self.assertEqual(reply.committed, intent.target)
        self.assertIsNone(reply.pending_operation_id)
        self.assertEqual(verifier.calls, [reply])

    def test_missing_or_rejecting_verifier_fails_closed(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        for verifier in (
            None,
            object(),
            TestOnlyVerifier(False),
            TestOnlyVerifier("yes"),
        ):
            with self.subTest(
                verifier=type(verifier).__name__
            ):
                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        reply,
                        verifier,
                    )

        class FailingVerifier:
            def verify_attestation(self, reply):
                raise OSError("Authority verifier unavailable")

        with self.assertRaises(ValueError):
            assess(
                module,
                intent,
                reply,
                FailingVerifier(),
            )

    def test_reply_identity_and_catalog_mismatch_rejected(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        replacements = (
            {"authority_id": "other-authority"},
            {"operation_id": "other-operation"},
            {
                "expected_committed": (
                    1,
                    intent.expected_committed[1],
                    "0" * 64,
                )
            },
            {
                "target": (
                    2,
                    intent.target[1],
                    "f" * 64,
                )
            },
            {"committed": intent.expected_committed},
        )

        for changes in replacements:
            with self.subTest(changes=repr(changes)):
                altered = dataclasses.replace(
                    reply,
                    **changes,
                )

                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        altered,
                        TestOnlyVerifier(True),
                    )

    def test_stale_generation_and_fencing_rejected(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        replay = dataclasses.replace(
            reply,
            generation=intent.expected_generation,
        )

        with self.assertRaises(ValueError):
            assess(
                module,
                intent,
                replay,
                TestOnlyVerifier(),
            )

        with self.assertRaises(ValueError):
            assess(
                module,
                intent,
                reply,
                TestOnlyVerifier(),
                minimum_generation=9,
            )

        for stale_fence in (100, 102):
            with self.subTest(fence=stale_fence):
                altered = dataclasses.replace(
                    reply,
                    fence_token=stale_fence,
                )

                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        altered,
                        TestOnlyVerifier(),
                    )

        with self.assertRaises(ValueError):
            assess(
                module,
                intent,
                reply,
                TestOnlyVerifier(),
                minimum_fence_token=102,
            )

    def test_invalid_publication_state_is_not_accepted(self):
        module = api()
        intent = make_intent(module)
        committed = make_reply(module, intent)
        prepared = make_reply(
            module,
            intent,
            prepared=True,
        )

        invalid = (
            dataclasses.replace(
                committed,
                status="unknown",
            ),
            dataclasses.replace(
                committed,
                pending_operation_id=OPERATION,
            ),
            dataclasses.replace(
                prepared,
                pending_operation_id=None,
            ),
            dataclasses.replace(
                prepared,
                committed=intent.target,
            ),
            dataclasses.replace(
                committed,
                evidence=b"",
            ),
            dataclasses.replace(
                committed,
                evidence="not-bytes",
            ),
        )

        for reply in invalid:
            with self.subTest(reply=repr(reply)):
                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        reply,
                        TestOnlyVerifier(True),
                    )

    def test_same_target_different_operation_id_is_not_proof(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        another_intent = dataclasses.replace(
            intent,
            operation_id="unrelated-publication",
        )

        # Matching target snapshots are not sufficient
        # evidence that another operation completed.
        with self.assertRaises(ValueError):
            assess(
                module,
                another_intent,
                reply,
                TestOnlyVerifier(True),
            )


    def test_reply_container_is_frozen(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        self.assertTrue(dataclasses.is_dataclass(reply))
        self.assertEqual(reply.operation_id, OPERATION)

        with self.assertRaises(
            (dataclasses.FrozenInstanceError, AttributeError)
        ):
            reply.operation_id = "substituted-operation"

        self.assertEqual(reply.operation_id, OPERATION)

    def test_untrusted_reply_object_types_are_rejected(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        invalid = (
            None,
            object(),
            dataclasses.asdict(reply),
            intent,
            "committed",
        )

        for candidate in invalid:
            with self.subTest(
                reply_type=type(candidate).__name__
            ):
                verifier = TestOnlyVerifier(True)

                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        candidate,
                        verifier,
                    )

                self.assertEqual(verifier.calls, [])

    def test_verifier_requires_exact_boolean_true(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        rejected_answers = (
            None,
            False,
            1,
            "True",
            [],
            {},
        )

        for answer in rejected_answers:
            with self.subTest(answer=repr(answer)):
                verifier = TestOnlyVerifier(answer)

                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        reply,
                        verifier,
                    )

                self.assertEqual(
                    verifier.calls,
                    [reply],
                )

        verifier = TestOnlyVerifier(True)

        self.assertEqual(
            assess(
                module,
                intent,
                reply,
                verifier,
            ),
            module.AuthorityReplyStatus.COMMITTED,
        )

        self.assertEqual(verifier.calls, [reply])

    def test_verifier_exceptions_fail_closed(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        class RaisingVerifier:
            def __init__(self, exception_type):
                self.exception_type = exception_type
                self.calls = 0

            def verify_attestation(self, reply):
                self.calls += 1
                raise self.exception_type(
                    "Injected verifier failure."
                )

        for exception_type in (
            OSError,
            RuntimeError,
            ValueError,
        ):
            with self.subTest(
                exception=exception_type.__name__
            ):
                verifier = RaisingVerifier(
                    exception_type
                )

                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        reply,
                        verifier,
                    )

                self.assertEqual(verifier.calls, 1)

    def test_invalid_structure_never_reaches_verifier(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        malformed_replies = (
            dataclasses.replace(
                reply,
                operation_id="different-operation",
            ),
            dataclasses.replace(
                reply,
                authority_id="different-authority",
            ),
            dataclasses.replace(
                reply,
                committed=intent.expected_committed,
            ),
            dataclasses.replace(
                reply,
                target=(
                    "invalid",
                    reply.target[1],
                    reply.target[2],
                ),
            ),
            dataclasses.replace(
                reply,
                evidence=b"",
            ),
            dataclasses.replace(
                reply,
                status="committed",
            ),
        )

        for candidate in malformed_replies:
            with self.subTest(reply=repr(candidate)):
                verifier = TestOnlyVerifier(True)

                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        candidate,
                        verifier,
                    )

                self.assertEqual(
                    verifier.calls,
                    [],
                )

    def test_advanced_generation_floor_rejects_replay(self):
        module = api()
        intent = make_intent(module)

        prepared = make_reply(
            module,
            intent,
            prepared=True,
        )

        committed = make_reply(
            module,
            intent,
            prepared=False,
        )

        self.assertEqual(prepared.generation, 8)
        self.assertEqual(committed.generation, 9)

        self.assertEqual(
            assess(
                module,
                intent,
                prepared,
                TestOnlyVerifier(True),
                minimum_generation=7,
            ),
            module.AuthorityReplyStatus.PREPARED,
        )

        # After the trusted minimum advances to 8,
        # the old PREPARED reply must not be accepted.
        with self.assertRaises(ValueError):
            assess(
                module,
                intent,
                prepared,
                TestOnlyVerifier(True),
                minimum_generation=8,
            )

        self.assertEqual(
            assess(
                module,
                intent,
                committed,
                TestOnlyVerifier(True),
                minimum_generation=8,
            ),
            module.AuthorityReplyStatus.COMMITTED,
        )

        with self.assertRaises(ValueError):
            assess(
                module,
                intent,
                committed,
                TestOnlyVerifier(True),
                minimum_generation=9,
            )

    def test_control_characters_and_long_ids_rejected(self):
        module = api()
        intent = make_intent(module)

        invalid_changes = (
            {"authority_id": "a" * 257},
            {"operation_id": "o" * 257},
            {"authority_id": "bad" + chr(0) + "id"},
            {"authority_id": "bad" + chr(127)},
            {"operation_id": "line" + chr(10) + "break"},
            {"operation_id": "tab" + chr(9) + "id"},
        )

        for changes in invalid_changes:
            with self.subTest(changes=repr(changes)):
                with self.assertRaises(ValueError):
                    dataclasses.replace(intent, **changes)

    def test_malformed_generations_and_fences_rejected(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        invalid_reply_fields = (
            {"generation": None},
            {"generation": True},
            {"generation": 7.0},
            {"generation": -1},
            {"generation": 7},
            {"fence_token": None},
            {"fence_token": True},
            {"fence_token": "101"},
            {"fence_token": 0},
            {"fence_token": 100},
            {"fence_token": 102},
        )

        for changes in invalid_reply_fields:
            with self.subTest(changes=repr(changes)):
                altered = dataclasses.replace(
                    reply,
                    **changes,
                )

                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        altered,
                        TestOnlyVerifier(True),
                    )

        invalid_minimum_generations = (
            None,
            True,
            -1,
            7.0,
        )

        for value in invalid_minimum_generations:
            with self.subTest(
                minimum_generation=repr(value)
            ):
                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        reply,
                        TestOnlyVerifier(True),
                        minimum_generation=value,
                    )

        invalid_minimum_fences = (
            None,
            True,
            0,
            "101",
        )

        for value in invalid_minimum_fences:
            with self.subTest(
                minimum_fence_token=repr(value)
            ):
                with self.assertRaises(ValueError):
                    assess(
                        module,
                        intent,
                        reply,
                        TestOnlyVerifier(True),
                        minimum_fence_token=value,
                    )

    def test_permissive_test_verifier_is_not_authentication(self):
        module = api()
        intent = make_intent(module)
        reply = make_reply(module, intent)

        fabricated = dataclasses.replace(
            reply,
            evidence=b"arbitrary-unverified-evidence",
        )

        permissive_verifier = TestOnlyVerifier(True)

        # This result is intentionally accepted by the
        # experimental contract because the caller
        # supplied a verifier that approves everything.
        #
        # The test documents a security boundary.
        # It does NOT demonstrate authentic evidence.
        self.assertEqual(
            assess(
                module,
                intent,
                fabricated,
                permissive_verifier,
            ),
            module.AuthorityReplyStatus.COMMITTED,
        )

        self.assertEqual(
            permissive_verifier.calls,
            [fabricated],
        )

        rejecting_verifier = TestOnlyVerifier(False)

        with self.assertRaises(ValueError):
            assess(
                module,
                intent,
                fabricated,
                rejecting_verifier,
            )

        self.assertEqual(
            rejecting_verifier.calls,
            [fabricated],
        )


if __name__ == "__main__":
    unittest.main()
