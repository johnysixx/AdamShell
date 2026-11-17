"""A44 pinned Ed25519 authority verifier contracts.

A pinned key is trusted ONLY if its provisioning source
is independently authenticated and protected.

These tests use ephemeral private keys in memory.
No production secret or persistent trust root is created.
"""

import dataclasses
import importlib
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)

from core.existence import (
    history_receipt_trust_independent_authority_contract
    as contract,
)

from core.existence.history_receipt_trust_authority_evidence import (
    canonical_authority_reply_bytes,
)

from test_a44_independent_authority_contract import (
    AUTHORITY,
    assess,
    make_intent,
    make_reply,
)


def api():
    return importlib.import_module(
        "core.existence."
        "history_receipt_trust_ed25519_verifier"
    )


def public_bytes(private_key):
    return private_key.public_key().public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )


def pinned(keys):
    return api().PinnedEd25519AuthorityVerifier.from_pinned_keys(
        keys
    )


def signed_reply(private_key, *, prepared=False):
    intent = make_intent(contract)

    template = make_reply(
        contract,
        intent,
        prepared=prepared,
    )

    signature = private_key.sign(
        canonical_authority_reply_bytes(template)
    )

    return intent, dataclasses.replace(
        template,
        evidence=signature,
    )


class A44PinnedEd25519VerifierTests(unittest.TestCase):

    def test_valid_committed_signature_from_pinned_authority(self):
        private_key = Ed25519PrivateKey.generate()
        intent, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        self.assertEqual(len(reply.evidence), 64)
        self.assertIs(
            verifier.verify_attestation(reply),
            True,
        )
        self.assertEqual(reply.authority_id, intent.authority_id)

    def test_valid_prepared_signature_from_pinned_authority(self):
        private_key = Ed25519PrivateKey.generate()
        intent, reply = signed_reply(
            private_key,
            prepared=True,
        )

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        self.assertIs(
            verifier.verify_attestation(reply),
            True,
        )
        self.assertIs(
            reply.status,
            contract.AuthorityReplyStatus.PREPARED,
        )
        self.assertEqual(
            reply.pending_operation_id,
            intent.operation_id,
        )

    def test_unknown_authority_identity_is_rejected(self):
        private_key = Ed25519PrivateKey.generate()
        _, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        unknown = dataclasses.replace(
            reply,
            authority_id="unregistered-authority",
        )

        self.assertIs(
            verifier.verify_attestation(unknown),
            False,
        )

        other_registry = pinned({
            "unrelated-authority": public_bytes(private_key)
        })

        self.assertIs(
            other_registry.verify_attestation(reply),
            False,
        )

    def test_wrong_key_and_attacker_signature_are_rejected(self):
        trusted = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()

        _, trusted_reply = signed_reply(trusted)
        _, attacker_reply = signed_reply(attacker)

        verifier = pinned({
            AUTHORITY: public_bytes(trusted)
        })

        self.assertIs(
            verifier.verify_attestation(trusted_reply),
            True,
        )

        self.assertIs(
            verifier.verify_attestation(attacker_reply),
            False,
        )

        wrong_verifier = pinned({
            AUTHORITY: public_bytes(attacker)
        })

        self.assertIs(
            wrong_verifier.verify_attestation(trusted_reply),
            False,
        )

    def test_semantic_mutations_invalidate_signature(self):
        private_key = Ed25519PrivateKey.generate()
        intent, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        target = reply.target

        changed_target = (
            target[0],
            target[1],
            "0" * 64
            if target[2] != "0" * 64
            else "1" * 64,
        )

        variants = (
            dataclasses.replace(
                reply,
                operation_id="another-operation",
            ),
            dataclasses.replace(
                reply,
                expected_committed=(
                    intent.expected_committed[0],
                    intent.expected_committed[1],
                    "f" * 64,
                ),
            ),
            dataclasses.replace(
                reply,
                target=changed_target,
                committed=changed_target,
            ),
            dataclasses.replace(
                reply,
                generation=reply.generation + 1,
            ),
            dataclasses.replace(
                reply,
                fence_token=reply.fence_token + 1,
            ),
            dataclasses.replace(
                reply,
                status=contract.AuthorityReplyStatus.PREPARED,
                committed=intent.expected_committed,
                pending_operation_id=intent.operation_id,
            ),
        )

        baseline = canonical_authority_reply_bytes(reply)

        for altered in variants:
            with self.subTest(reply=repr(altered)):
                self.assertNotEqual(
                    canonical_authority_reply_bytes(altered),
                    baseline,
                )
                self.assertIs(
                    verifier.verify_attestation(altered),
                    False,
                )

    def test_malformed_signature_evidence_fails_closed(self):
        private_key = Ed25519PrivateKey.generate()
        _, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        invalid_evidence = (
            None,
            "",
            b"",
            b"x" * 63,
            b"x" * 65,
            public_bytes(private_key) + reply.evidence,
            bytearray(reply.evidence),
            list(reply.evidence),
        )

        for evidence in invalid_evidence:
            with self.subTest(
                evidence_type=type(evidence).__name__,
                evidence_length=(
                    len(evidence)
                    if hasattr(evidence, "__len__")
                    else None
                ),
            ):
                altered = dataclasses.replace(
                    reply,
                    evidence=evidence,
                )

                self.assertIs(
                    verifier.verify_attestation(altered),
                    False,
                )

    def test_invalid_reply_objects_fail_closed(self):
        private_key = Ed25519PrivateKey.generate()
        intent, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        invalid = (
            None,
            object(),
            intent,
            dataclasses.asdict(reply),
            dataclasses.replace(
                reply,
                status="committed",
            ),
            dataclasses.replace(
                reply,
                committed=reply.expected_committed,
            ),
        )

        for candidate in invalid:
            with self.subTest(
                candidate_type=type(candidate).__name__
            ):
                self.assertIs(
                    verifier.verify_attestation(candidate),
                    False,
                )

    def test_invalid_pinned_key_catalog_is_rejected(self):
        private_key = Ed25519PrivateKey.generate()
        key = public_bytes(private_key)

        invalid = (
            None,
            {},
            [],
            {AUTHORITY: None},
            {AUTHORITY: ""},
            {AUTHORITY: b""},
            {AUTHORITY: bytes(31)},
            {AUTHORITY: bytes(33)},
            {AUTHORITY: bytearray(key)},
            {"": key},
            {" padded ": key},
            {"bad\nidentity": key},
            {"x" * 257: key},
            {7: key},
        )

        for catalog in invalid:
            with self.subTest(
                catalog=repr(catalog)
            ):
                with self.assertRaises(ValueError):
                    pinned(catalog)

    def test_pinned_registry_detaches_mutable_input(self):
        trusted = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()

        original_public_key = public_bytes(trusted)

        configuration = {
            AUTHORITY: original_public_key
        }

        verifier = pinned(configuration)

        configuration[AUTHORITY] = public_bytes(attacker)

        _, trusted_reply = signed_reply(trusted)
        _, attacker_reply = signed_reply(attacker)

        self.assertIs(
            verifier.verify_attestation(trusted_reply),
            True,
        )

        self.assertIs(
            verifier.verify_attestation(attacker_reply),
            False,
        )

        configuration.clear()

        self.assertIs(
            verifier.verify_attestation(trusted_reply),
            True,
        )

    def test_existing_attested_protocol_accepts_pinned_verifier(self):
        trusted = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()

        intent, reply = signed_reply(trusted)

        verifier = pinned({
            AUTHORITY: public_bytes(trusted)
        })

        self.assertIs(
            assess(
                contract,
                intent,
                reply,
                verifier,
                minimum_generation=8,
            ),
            contract.AuthorityReplyStatus.COMMITTED,
        )

        _, forged = signed_reply(attacker)

        with self.assertRaises(ValueError):
            assess(
                contract,
                intent,
                forged,
                verifier,
                minimum_generation=8,
            )

    def test_valid_signature_does_not_bypass_replay_guards(self):
        private_key = Ed25519PrivateKey.generate()
        intent, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        self.assertIs(
            verifier.verify_attestation(reply),
            True,
        )

        with self.assertRaises(ValueError):
            assess(
                contract,
                intent,
                reply,
                verifier,
                minimum_generation=reply.generation,
            )

        with self.assertRaises(ValueError):
            assess(
                contract,
                intent,
                reply,
                verifier,
                minimum_fence_token=intent.fence_token + 1,
            )

    def test_external_key_provisioning_is_a_trust_boundary(self):
        trusted = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()

        _, trusted_reply = signed_reply(trusted)
        _, attacker_reply = signed_reply(attacker)

        trusted_verifier = pinned({
            AUTHORITY: public_bytes(trusted)
        })

        attacker_configured_verifier = pinned({
            AUTHORITY: public_bytes(attacker)
        })

        self.assertIs(
            trusted_verifier.verify_attestation(attacker_reply),
            False,
        )

        # Intentionally demonstrates the provisioning
        # boundary, not a secure enrollment process.
        # An attacker-controlled pin makes the attacker
        # appear cryptographically authorized.
        self.assertIs(
            attacker_configured_verifier.verify_attestation(
                attacker_reply
            ),
            True,
        )

        self.assertIs(
            attacker_configured_verifier.verify_attestation(
                trusted_reply
            ),
            False,
        )


    def test_bit_flips_across_signature_rejected(self):
        private_key = Ed25519PrivateKey.generate()
        _, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        self.assertIs(
            verifier.verify_attestation(reply),
            True,
        )

        for index in (
            0, 1, 7, 15, 31, 32, 47, 62, 63
        ):
            with self.subTest(byte_index=index):
                corrupted = bytearray(reply.evidence)
                corrupted[index] ^= 1

                altered = dataclasses.replace(
                    reply,
                    evidence=bytes(corrupted),
                )

                self.assertIs(
                    verifier.verify_attestation(altered),
                    False,
                )

    def test_signature_envelope_injection_rejected(self):
        private_key = Ed25519PrivateKey.generate()
        _, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        signature = reply.evidence
        key = public_bytes(private_key)

        invalid = (
            b"x" + signature,
            signature + b"x",
            signature[:-1],
            signature + key,
            key + signature,
            b"Ed25519:" + signature,
            b"",
            bytes(64),
            bytearray(signature),
            memoryview(signature),
        )

        for evidence in invalid:
            with self.subTest(
                evidence_type=type(evidence).__name__,
                evidence_length=len(evidence),
            ):
                altered = dataclasses.replace(
                    reply,
                    evidence=evidence,
                )

                self.assertIs(
                    verifier.verify_attestation(altered),
                    False,
                )

    def test_cross_domain_and_version_signatures_rejected(self):
        import json

        private_key = Ed25519PrivateKey.generate()
        _, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        valid_payload = canonical_authority_reply_bytes(
            reply
        )

        message = json.loads(
            valid_payload.decode("ascii")
        )

        for changes in (
            {"domain": "unrelated.protocol"},
            {"version": 2},
            {
                "domain": "unrelated.protocol",
                "version": 2,
            },
        ):
            with self.subTest(changes=changes):
                altered_message = dict(message)
                altered_message.update(changes)

                foreign_payload = json.dumps(
                    altered_message,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                    allow_nan=False,
                ).encode("ascii")

                self.assertNotEqual(
                    foreign_payload,
                    valid_payload,
                )

                foreign_signature = private_key.sign(
                    foreign_payload
                )

                forged = dataclasses.replace(
                    reply,
                    evidence=foreign_signature,
                )

                self.assertIs(
                    verifier.verify_attestation(forged),
                    False,
                )

        self.assertIs(
            verifier.verify_attestation(reply),
            True,
        )

    def test_all_snapshot_components_bound_to_signature(self):
        private_key = Ed25519PrivateKey.generate()
        _, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        old = reply.expected_committed
        target = reply.target

        def other_digest(value):
            return (
                "0" * 64
                if value != "0" * 64
                else "1" * 64
            )

        altered_old = (
            old[0],
            old[1],
            other_digest(old[2]),
        )

        altered_target = (
            target[0],
            target[1],
            other_digest(target[2]),
        )

        altered_sources = other_digest(old[1])

        variants = (
            (
                "predecessor_catalog",
                dataclasses.replace(
                    reply,
                    expected_committed=altered_old,
                ),
            ),
            (
                "target_catalog",
                dataclasses.replace(
                    reply,
                    target=altered_target,
                    committed=altered_target,
                ),
            ),
            (
                "source_identity_digest",
                dataclasses.replace(
                    reply,
                    expected_committed=(
                        old[0],
                        altered_sources,
                        old[2],
                    ),
                    target=(
                        target[0],
                        altered_sources,
                        target[2],
                    ),
                    committed=(
                        target[0],
                        altered_sources,
                        target[2],
                    ),
                ),
            ),
            (
                "target_revision",
                dataclasses.replace(
                    reply,
                    target=(
                        target[0] + 1,
                        target[1],
                        target[2],
                    ),
                    committed=(
                        target[0] + 1,
                        target[1],
                        target[2],
                    ),
                ),
            ),
        )

        baseline = canonical_authority_reply_bytes(
            reply
        )

        for name, altered in variants:
            with self.subTest(field=name):
                self.assertNotEqual(
                    canonical_authority_reply_bytes(altered),
                    baseline,
                )

                self.assertIs(
                    verifier.verify_attestation(altered),
                    False,
                )

    def test_signed_prepared_committed_state_swap_rejected(self):
        private_key = Ed25519PrivateKey.generate()

        intent, prepared = signed_reply(
            private_key,
            prepared=True,
        )

        _, committed = signed_reply(
            private_key,
            prepared=False,
        )

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        self.assertIs(
            verifier.verify_attestation(prepared),
            True,
        )

        self.assertIs(
            verifier.verify_attestation(committed),
            True,
        )

        falsely_committed = dataclasses.replace(
            prepared,
            status=contract.AuthorityReplyStatus.COMMITTED,
            committed=intent.target,
            pending_operation_id=None,
        )

        falsely_prepared = dataclasses.replace(
            committed,
            status=contract.AuthorityReplyStatus.PREPARED,
            committed=intent.expected_committed,
            pending_operation_id=intent.operation_id,
        )

        self.assertIs(
            verifier.verify_attestation(falsely_committed),
            False,
        )

        self.assertIs(
            verifier.verify_attestation(falsely_prepared),
            False,
        )

    def test_multiple_authorities_restrict_keys_and_identities(self):
        first_key = Ed25519PrivateKey.generate()
        second_key = Ed25519PrivateKey.generate()

        _, first_reply = signed_reply(first_key)

        _, second_template = signed_reply(second_key)

        second_template = dataclasses.replace(
            second_template,
            authority_id="second-authority",
        )

        second_reply = dataclasses.replace(
            second_template,
            evidence=second_key.sign(
                canonical_authority_reply_bytes(
                    second_template
                )
            ),
        )

        verifier = pinned({
            AUTHORITY: public_bytes(first_key),
            "second-authority": public_bytes(second_key),
        })

        self.assertIs(
            verifier.verify_attestation(first_reply),
            True,
        )

        self.assertIs(
            verifier.verify_attestation(second_reply),
            True,
        )

        wrong_signature_for_first = dataclasses.replace(
            first_reply,
            evidence=second_reply.evidence,
        )

        wrong_signature_for_second = dataclasses.replace(
            second_reply,
            evidence=first_reply.evidence,
        )

        self.assertIs(
            verifier.verify_attestation(
                wrong_signature_for_first
            ),
            False,
        )

        self.assertIs(
            verifier.verify_attestation(
                wrong_signature_for_second
            ),
            False,
        )

    def test_shared_key_identity_separation_requires_new_signature(self):
        private_key = Ed25519PrivateKey.generate()

        _, original = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key),
            "second-authority": public_bytes(private_key),
        })

        retitled = dataclasses.replace(
            original,
            authority_id="second-authority",
        )

        # The same public key may be provisioned for
        # multiple IDs. The original signature must
        # still bind the original identity.
        self.assertIs(
            verifier.verify_attestation(retitled),
            False,
        )

        newly_signed = dataclasses.replace(
            retitled,
            evidence=private_key.sign(
                canonical_authority_reply_bytes(
                    retitled
                )
            ),
        )

        self.assertIs(
            verifier.verify_attestation(newly_signed),
            True,
        )

        # This demonstrates that shared-key provisioning
        # is a trust-policy decision, not an identity
        # separation guarantee of the verifier.

    def test_mapping_and_bytes_subtypes_cannot_extend_pins(self):
        from types import MappingProxyType

        private_key = Ed25519PrivateKey.generate()
        key = public_bytes(private_key)

        class DictionarySubclass(dict):
            pass

        class BytesSubclass(bytes):
            pass

        invalid = (
            DictionarySubclass({AUTHORITY: key}),
            MappingProxyType({AUTHORITY: key}),
            {AUTHORITY: BytesSubclass(key)},
            {AUTHORITY: memoryview(key)},
            {"bad" + chr(10) + "identity": key},
            {"bad" + chr(0) + "identity": key},
        )

        for catalog in invalid:
            with self.subTest(
                catalog_type=type(catalog).__name__,
                catalog=repr(catalog),
            ):
                with self.assertRaises(ValueError):
                    pinned(catalog)

    def test_malformed_semantic_replies_fail_closed(self):
        private_key = Ed25519PrivateKey.generate()
        _, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        target = reply.target

        malformed = (
            dataclasses.replace(
                reply,
                authority_id=" padded ",
            ),
            dataclasses.replace(
                reply,
                operation_id="line" + chr(10) + "break",
            ),
            dataclasses.replace(
                reply,
                generation=True,
            ),
            dataclasses.replace(
                reply,
                generation=-1,
            ),
            dataclasses.replace(
                reply,
                fence_token=True,
            ),
            dataclasses.replace(
                reply,
                fence_token=0,
            ),
            dataclasses.replace(
                reply,
                status="committed",
            ),
            dataclasses.replace(
                reply,
                target=list(target),
            ),
            dataclasses.replace(
                reply,
                target=(
                    target[0],
                    "0" * 64,
                    target[2],
                ),
            ),
            dataclasses.replace(
                reply,
                committed=reply.expected_committed,
            ),
        )

        for candidate in malformed:
            with self.subTest(reply=repr(candidate)):
                self.assertIs(
                    verifier.verify_attestation(candidate),
                    False,
                )

    def test_valid_signature_still_depends_on_trusted_floors(self):
        private_key = Ed25519PrivateKey.generate()
        intent, reply = signed_reply(private_key)

        verifier = pinned({
            AUTHORITY: public_bytes(private_key)
        })

        self.assertIs(
            verifier.verify_attestation(reply),
            True,
        )

        # An authenticated historical reply is not
        # automatically fresh. The trusted generation
        # and fencing bounds must be maintained elsewhere.
        self.assertIs(
            assess(
                contract,
                intent,
                reply,
                verifier,
                minimum_generation=8,
            ),
            contract.AuthorityReplyStatus.COMMITTED,
        )

        with self.assertRaises(ValueError):
            assess(
                contract,
                intent,
                reply,
                verifier,
                minimum_generation=reply.generation,
            )

        with self.assertRaises(ValueError):
            assess(
                contract,
                intent,
                reply,
                verifier,
                minimum_fence_token=intent.fence_token + 1,
            )

        # Lowering the caller-supplied floor permits
        # the historical reply to be accepted again.
        # This is why the floor must be independently
        # maintained and rollback-resistant.
        self.assertIs(
            assess(
                contract,
                intent,
                reply,
                verifier,
                minimum_generation=8,
            ),
            contract.AuthorityReplyStatus.COMMITTED,
        )


if __name__ == "__main__":
    unittest.main()
