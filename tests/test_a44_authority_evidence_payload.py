"""A44 canonical signed authority-reply payload contracts.

The payload is the message that a future independent
authority will sign and a trusted verifier will check.

These tests do not implement cryptographic signatures,
key provisioning, revocation, or rollback resistance.
"""

import dataclasses
import importlib
import json
import unittest

from core.existence import (
    history_receipt_trust_independent_authority_contract
    as contract,
)
from test_a44_independent_authority_contract import (
    make_intent,
    make_reply,
)


DOMAIN = "adam-shell.receipt-trust.authority-reply"
VERSION = 1


def api():
    return importlib.import_module(
        "core.existence."
        "history_receipt_trust_authority_evidence"
    )


def sample_reply(*, prepared=False):
    intent = make_intent(contract)
    return make_reply(
        contract,
        intent,
        prepared=prepared,
    )


def canonical(reply):
    return api().canonical_authority_reply_bytes(reply)


def decoded(reply):
    return json.loads(canonical(reply).decode("utf-8"))


class A44AuthorityEvidencePayloadTests(unittest.TestCase):

    def test_canonical_payload_has_domain_version_and_complete_fields(self):
        reply = sample_reply()
        payload = canonical(reply)

        self.assertIs(type(payload), bytes)

        message = json.loads(payload.decode("utf-8"))

        self.assertEqual(
            set(message),
            {
                "domain",
                "version",
                "authority_id",
                "operation_id",
                "expected_committed",
                "target",
                "committed",
                "pending_operation_id",
                "status",
                "generation",
                "fence_token",
            },
        )

        self.assertEqual(message["domain"], DOMAIN)
        self.assertIs(type(message["version"]), int)
        self.assertEqual(message["version"], VERSION)
        self.assertEqual(
            message["authority_id"],
            reply.authority_id,
        )
        self.assertEqual(
            message["operation_id"],
            reply.operation_id,
        )

        self.assertNotIn("evidence", message)

    def test_canonical_json_is_deterministic_and_minimal(self):
        reply = sample_reply()

        first = canonical(reply)
        second = canonical(reply)

        self.assertEqual(first, second)

        parsed = json.loads(first.decode("utf-8"))

        expected = json.dumps(
            parsed,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")

        self.assertEqual(first, expected)
        self.assertNotIn(b"\n", first)

    def test_all_snapshot_components_are_explicitly_bound(self):
        reply = sample_reply()
        message = decoded(reply)

        for field in (
            "expected_committed",
            "target",
            "committed",
        ):
            with self.subTest(field=field):
                actual = message[field]
                original = getattr(reply, field)

                self.assertEqual(
                    set(actual),
                    {
                        "revision",
                        "source_ids_digest",
                        "catalog_digest",
                    },
                )

                self.assertEqual(
                    actual["revision"],
                    original[0],
                )

                self.assertEqual(
                    actual["source_ids_digest"],
                    original[1],
                )

                self.assertEqual(
                    actual["catalog_digest"],
                    original[2],
                )

    def test_changing_authority_or_operation_changes_payload(self):
        reply = sample_reply()
        original = canonical(reply)

        variants = (
            dataclasses.replace(
                reply,
                authority_id="different-authority",
            ),
            dataclasses.replace(
                reply,
                operation_id="different-operation",
            ),
        )

        for altered in variants:
            with self.subTest(
                operation=altered.operation_id,
                authority=altered.authority_id,
            ):
                self.assertNotEqual(
                    canonical(altered),
                    original,
                )

    def test_generation_and_fence_are_signed_fields(self):
        reply = sample_reply()
        original = canonical(reply)

        altered_generation = dataclasses.replace(
            reply,
            generation=reply.generation + 1,
        )

        altered_fence = dataclasses.replace(
            reply,
            fence_token=reply.fence_token + 1,
        )

        self.assertNotEqual(
            canonical(altered_generation),
            original,
        )

        self.assertNotEqual(
            canonical(altered_fence),
            original,
        )

        self.assertEqual(
            decoded(altered_generation)["generation"],
            reply.generation + 1,
        )

        self.assertEqual(
            decoded(altered_fence)["fence_token"],
            reply.fence_token + 1,
        )

    def test_prepared_and_committed_are_distinct_signed_states(self):
        prepared = sample_reply(prepared=True)
        committed = sample_reply(prepared=False)

        prepared_message = decoded(prepared)
        committed_message = decoded(committed)

        self.assertEqual(
            prepared_message["status"],
            "prepared",
        )

        self.assertEqual(
            committed_message["status"],
            "committed",
        )

        self.assertEqual(
            prepared_message["pending_operation_id"],
            prepared.operation_id,
        )

        self.assertIsNone(
            committed_message["pending_operation_id"]
        )

        self.assertEqual(
            prepared_message["committed"]["revision"],
            prepared.expected_committed[0],
        )

        self.assertEqual(
            committed_message["committed"]["revision"],
            committed.target[0],
        )

        self.assertNotEqual(
            canonical(prepared),
            canonical(committed),
        )

    def test_evidence_is_excluded_from_signed_payload(self):
        reply = sample_reply()

        unsigned = dataclasses.replace(
            reply,
            evidence=b"",
        )

        alternative = dataclasses.replace(
            reply,
            evidence=b"another-signature-or-proof",
        )

        self.assertEqual(
            canonical(reply),
            canonical(unsigned),
        )

        self.assertEqual(
            canonical(reply),
            canonical(alternative),
        )

        self.assertNotIn(
            b"another-signature-or-proof",
            canonical(alternative),
        )

    def test_malformed_reply_inputs_fail_closed(self):
        reply = sample_reply()

        malformed = (
            None,
            object(),
            dataclasses.asdict(reply),
            dataclasses.replace(
                reply,
                status="committed",
            ),
            dataclasses.replace(
                reply,
                authority_id=" padded ",
            ),
            dataclasses.replace(
                reply,
                operation_id="bad\noperation",
            ),
            dataclasses.replace(
                reply,
                generation=True,
            ),
            dataclasses.replace(
                reply,
                fence_token=True,
            ),
            dataclasses.replace(
                reply,
                target=list(reply.target),
            ),
            dataclasses.replace(
                reply,
                committed=reply.expected_committed,
            ),
            dataclasses.replace(
                reply,
                pending_operation_id=reply.operation_id,
            ),
        )

        for candidate in malformed:
            with self.subTest(
                candidate=repr(candidate)
            ):
                with self.assertRaises(ValueError):
                    canonical(candidate)

    def test_unicode_ids_have_stable_ascii_encoding(self):
        reply = sample_reply()

        localized = dataclasses.replace(
            reply,
            authority_id="autorita-zluta-?",
            operation_id="operace-?ern?",
        )

        first = canonical(localized)
        second = canonical(localized)

        self.assertEqual(first, second)

        # Escaped Unicode avoids encoding-dependent
        # byte representations in signed messages.
        first.decode("ascii")

        message = json.loads(first.decode("ascii"))

        self.assertEqual(
            message["authority_id"],
            "autorita-zluta-?",
        )

        self.assertEqual(
            message["operation_id"],
            "operace-?ern?",
        )


    def test_fixed_version_one_golden_vector(self):
        import hashlib

        old = (7, "b" * 64, "a" * 64)
        new = (8, "b" * 64, "c" * 64)

        reply = contract.AuthorityAttestedReply(
            authority_id="fixed-authority",
            operation_id="fixed-operation",
            expected_committed=old,
            target=new,
            committed=new,
            pending_operation_id=None,
            status=contract.AuthorityReplyStatus.COMMITTED,
            generation=12,
            fence_token=90,
            evidence=b"test-signature",
        )

        payload = canonical(reply)

        # Fixed external reference for the v1 byte contract.
        # Do not derive this expectation by calling the
        # implementation under test.
        self.assertEqual(len(payload), 813)

        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            "c30cc7ccdb0fcd3aeae49e3baa2ad958"
            "ad35e2a6500ef353566cb4228ac5d341",
        )

        self.assertEqual(
            decoded(reply)["domain"],
            DOMAIN,
        )

        self.assertEqual(
            decoded(reply)["version"],
            VERSION,
        )

    def test_completed_semantic_field_mutations_change_bytes(self):
        reply = sample_reply()
        old = reply.expected_committed
        target = reply.target

        old_catalog = (
            "0" * 64 if old[2] != "0" * 64 else "1" * 64
        )
        target_catalog = (
            "1" * 64 if target[2] != "1" * 64 else "2" * 64
        )
        new_sources = (
            "2" * 64 if old[1] != "2" * 64 else "3" * 64
        )

        changed_old = (old[0], old[1], old_catalog)
        changed_target = (
            target[0],
            target[1],
            target_catalog,
        )

        variants = (
            ("authority", dataclasses.replace(
                reply,
                authority_id="another-authority",
            )),
            ("operation", dataclasses.replace(
                reply,
                operation_id="another-operation",
            )),
            ("predecessor", dataclasses.replace(
                reply,
                expected_committed=changed_old,
            )),
            ("target", dataclasses.replace(
                reply,
                target=changed_target,
                committed=changed_target,
            )),
            ("sources", dataclasses.replace(
                reply,
                expected_committed=(
                    old[0], new_sources, old[2]
                ),
                target=(
                    target[0], new_sources, target[2]
                ),
                committed=(
                    target[0], new_sources, target[2]
                ),
            )),
            ("generation", dataclasses.replace(
                reply,
                generation=reply.generation + 1,
            )),
            ("fence", dataclasses.replace(
                reply,
                fence_token=reply.fence_token + 1,
            )),
        )

        baseline = canonical(reply)

        for label, altered in variants:
            with self.subTest(field=label):
                self.assertNotEqual(
                    canonical(altered),
                    baseline,
                )

    def test_prepared_semantic_field_mutations_change_bytes(self):
        reply = sample_reply(prepared=True)
        old = reply.expected_committed
        target = reply.target

        new_old = (
            old[0],
            old[1],
            "4" * 64 if old[2] != "4" * 64
            else "5" * 64,
        )

        new_target = (
            target[0],
            target[1],
            "6" * 64 if target[2] != "6" * 64
            else "7" * 64,
        )

        variants = (
            ("operation", dataclasses.replace(
                reply,
                operation_id="new-prepared-operation",
                pending_operation_id="new-prepared-operation",
            )),
            ("predecessor-and-committed", dataclasses.replace(
                reply,
                expected_committed=new_old,
                committed=new_old,
            )),
            ("target", dataclasses.replace(
                reply,
                target=new_target,
            )),
            ("generation", dataclasses.replace(
                reply,
                generation=reply.generation + 1,
            )),
            ("fence", dataclasses.replace(
                reply,
                fence_token=reply.fence_token + 1,
            )),
        )

        baseline = canonical(reply)

        for label, altered in variants:
            with self.subTest(field=label):
                self.assertNotEqual(
                    canonical(altered),
                    baseline,
                )

    def test_invalid_nested_snapshots_are_rejected(self):
        reply = sample_reply()
        old = reply.expected_committed
        target = reply.target

        variants = (
            {"expected_committed": None},
            {"expected_committed": list(old)},
            {"target": list(target)},
            {"target": dict(revision=2)},
            {"committed": list(reply.committed)},
            {"target": (
                True, target[1], target[2]
            )},
            {"target": (
                2.5, target[1], target[2]
            )},
            {"target": (
                old[0], target[1], target[2]
            )},
            {"target": (
                target[0], "A" * 64, target[2]
            )},
            {"target": (
                target[0], target[1], "invalid"
            )},
            {"target": (
                target[0], "0" * 64, target[2]
            )},
            {"committed": (
                reply.committed[0],
                reply.committed[1],
                "f" * 64
                if reply.committed[2] != "f" * 64
                else "e" * 64,
            )},
        )

        for changes in variants:
            with self.subTest(changes=repr(changes)):
                with self.assertRaises(ValueError):
                    canonical(
                        dataclasses.replace(
                            reply,
                            **changes,
                        )
                    )

    def test_status_and_pending_mismatches_are_rejected(self):
        committed = sample_reply()
        prepared = sample_reply(prepared=True)

        invalid = (
            dataclasses.replace(
                committed,
                status="committed",
            ),
            dataclasses.replace(
                committed,
                status=None,
            ),
            dataclasses.replace(
                committed,
                pending_operation_id=committed.operation_id,
            ),
            dataclasses.replace(
                committed,
                committed=committed.expected_committed,
            ),
            dataclasses.replace(
                prepared,
                pending_operation_id=None,
            ),
            dataclasses.replace(
                prepared,
                pending_operation_id="other-operation",
            ),
            dataclasses.replace(
                prepared,
                committed=prepared.target,
            ),
        )

        for reply in invalid:
            with self.subTest(reply=repr(reply)):
                with self.assertRaises(ValueError):
                    canonical(reply)

    def test_malformed_counters_are_rejected(self):
        reply = sample_reply()

        variants = (
            {"generation": True},
            {"generation": None},
            {"generation": -1},
            {"generation": 1.25},
            {"generation": "10"},
            {"fence_token": True},
            {"fence_token": None},
            {"fence_token": 0},
            {"fence_token": 1.25},
            {"fence_token": "101"},
        )

        for changes in variants:
            with self.subTest(changes=repr(changes)):
                with self.assertRaises(ValueError):
                    canonical(
                        dataclasses.replace(
                            reply,
                            **changes,
                        )
                    )

    def test_non_reply_containers_are_rejected(self):
        reply = sample_reply()

        invalid = (
            None,
            object(),
            {},
            dataclasses.asdict(reply),
            [],
            "committed",
            make_intent(contract),
        )

        for candidate in invalid:
            with self.subTest(
                candidate_type=type(candidate).__name__
            ):
                with self.assertRaises(ValueError):
                    canonical(candidate)

    def test_evidence_is_excluded_in_both_publication_states(self):
        for prepared in (False, True):
            with self.subTest(prepared=prepared):
                reply = sample_reply(prepared=prepared)
                baseline = canonical(reply)

                for evidence in (
                    b"",
                    b"another-signature",
                    None,
                    "untrusted-evidence",
                ):
                    altered = dataclasses.replace(
                        reply,
                        evidence=evidence,
                    )

                    self.assertEqual(
                        canonical(altered),
                        baseline,
                    )

        # This test covers payload construction only.
        # Final attestation validation must separately
        # reject missing or unauthentic evidence.

    def test_unicode_identity_bytes_are_not_implicitly_normalized(self):
        reply = sample_reply()

        composed = dataclasses.replace(
            reply,
            authority_id="autorita-" + chr(233),
        )

        decomposed = dataclasses.replace(
            reply,
            authority_id="autorita-e" + chr(769),
        )

        first = canonical(composed)
        second = canonical(decomposed)

        first.decode("ascii")
        second.decode("ascii")

        self.assertNotEqual(first, second)

        self.assertNotEqual(
            json.loads(first)["authority_id"],
            json.loads(second)["authority_id"],
        )

        # The protocol compares exact Unicode identity
        # strings. Provisioned authority identities must
        # use the same defined representation.


if __name__ == "__main__":
    unittest.main()
