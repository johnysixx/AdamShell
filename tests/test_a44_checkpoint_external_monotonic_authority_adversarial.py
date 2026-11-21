"""A44 adversarial signed monotonic authority client tests.

All signer and authority instances are volatile TEST DOUBLES.

The tests establish the client's behavior against malformed,
replayed or misleading signed responses. They cannot establish
the independent trust or persistence of a real authority.

In particular, a signer under attacker control can produce
consistent but false CAS and readback messages. This is
a documented trust limitation, not a client verification bug.

No production database, external service, key enrollment,
checkpoint restoration or republication is performed.
"""

import json
import sys
import unittest

from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_external_monotonic_authority as contract


OLD = contract.OLD
NEXT = contract.NEXT
GENERATION = contract.GENERATION
FENCE = contract.FENCE


def change_field(field, value):
    def transform(message):
        document = json.loads(message)
        document[field] = value
        return contract.canonical(document)

    return transform


def remove_field(field):
    def transform(message):
        document = json.loads(message)
        document.pop(field)
        return contract.canonical(document)

    return transform


class MutatingSignedAuthority(
    contract.SignedMemoryMonotonicAuthority
):
    """Re-sign deliberately altered messages with a valid key."""

    def __init__(
        self,
        signer,
        transform,
        *,
        operation="read",
    ):
        super().__init__(signer)

        self.transform = transform
        self.target_operation = operation

    def _signed(self, **arguments):
        original = super()._signed(**arguments)

        if arguments["operation"] != self.target_operation:
            return original

        message, _ = original

        mutated = self.transform(message)

        if type(mutated) is not bytes:
            raise AssertionError(
                "Adversarial transform must return bytes."
            )

        return mutated, self.signer.sign(mutated)


class InvalidPairAuthority(
    contract.SignedMemoryMonotonicAuthority
):
    def __init__(self, signer, response):
        super().__init__(signer)
        self.invalid_response = response

    def _signed(self, **arguments):
        if arguments["operation"] == "read":
            return self.invalid_response

        return super()._signed(**arguments)


class A44CheckpointExternalMonotonicAuthorityAdversarialTests(
    unittest.TestCase
):

    def setUp(self):
        self.fixture = (
            contract.A44CheckpointExternalMonotonicAuthorityContractTests(
                "test_signed_held_read_and_six_field_snapshot"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.authority = self.fixture.authority
        self.source = self.fixture.source

    def read(self, source=None):
        return self.fixture.read(
            self.source if source is None else source
        )

    def advance(self, source=None, **changes):
        return self.fixture.advance(
            self.source if source is None else source,
            **changes,
        )

    def injected(self, transform, *, operation="read"):
        backend = MutatingSignedAuthority(
            self.fixture.private,
            transform,
            operation=operation,
        )

        source = self.fixture.make_source(
            authority=backend,
        )

        return backend, source

    def assert_rejected_read(self, source):
        with self.assertRaises(ValueError):
            self.read(source)

    def test_noncanonical_duplicate_and_nonfinite_signed_json(
        self
    ):
        def duplicate_revision(message):
            original = b'"revision":40'

            if message.count(original) != 1:
                raise AssertionError(
                    "Unexpected signed revision encoding."
                )

            return message.replace(
                original,
                b'"revision":40,"revision":40',
                1,
            )

        def nonfinite_revision(message):
            original = b'"revision":40'

            if message.count(original) != 1:
                raise AssertionError(
                    "Unexpected signed revision encoding."
                )

            return message.replace(
                original,
                b'"revision":NaN',
                1,
            )

        def nonascii_identity(message):
            document = json.loads(message)
            document["root_id"] = "racine_\u00e9"

            return json.dumps(
                document,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")

        attacks = (
            ("trailing-newline", lambda raw: raw + b"\n"),
            ("duplicate-property", duplicate_revision),
            ("nonfinite-number", nonfinite_revision),
            ("nonascii-encoding", nonascii_identity),
            ("leading-whitespace", lambda raw: b" " + raw),
        )

        for name, transform in attacks:
            with self.subTest(attack=name):
                backend, source = self.injected(transform)

                self.assert_rejected_read(source)

                self.assertFalse(backend.active)
                self.assertEqual(backend.cas_calls, 0)

    def test_signed_identity_and_protocol_substitution(
        self
    ):
        attacks = (
            ("authority_id", "rogue_authority"),
            ("root_id", "rogue_root"),
            ("root_public_key_hex", "42" * 32),
            ("enrollment_epoch", contract.EPOCH + 1),
            ("challenge_hex", "ff" * 32),
            ("domain", "Unrelated/Protocol/v1"),
            ("version", 2),
            ("operation", "cas"),
            ("unexpected", "injected-property"),
        )

        for field, replacement in attacks:
            with self.subTest(field=field):
                backend, source = self.injected(
                    change_field(field, replacement)
                )

                self.assert_rejected_read(source)
                self.assertFalse(backend.active)

        for field in (
            "root_id",
            "challenge_hex",
            "authority_id",
        ):
            with self.subTest(missing=field):
                backend, source = self.injected(
                    remove_field(field)
                )

                self.assert_rejected_read(source)
                self.assertFalse(backend.active)

    def test_signed_counter_type_confusion_rejected(self):
        for field in (
            "revision",
            "generation",
            "fence_token",
            "enrollment_epoch",
        ):
            for value in (
                True,
                -1,
                "40",
                40.5,
            ):
                with self.subTest(
                    field=field,
                    value=repr(value),
                ):
                    backend, source = self.injected(
                        change_field(field, value)
                    )

                    self.assert_rejected_read(source)
                    self.assertFalse(backend.active)

    def test_malformed_signed_pairs_and_signatures_rejected(
        self
    ):
        malformed = (
            None,
            (),
            (b"incomplete",),
            (b"a", b"b" * 64, b"extra"),
            [b"a", b"b" * 64],
            (b"", b"b" * 64),
            (b"a", bytearray(b"b" * 64)),
            (b"a", b"short"),
            (b"x" * 4097, b"b" * 64),
        )

        for response in malformed:
            with self.subTest(response=repr(response)[:65]):
                backend = InvalidPairAuthority(
                    self.fixture.private,
                    response,
                )

                source = self.fixture.make_source(
                    authority=backend,
                )

                self.assert_rejected_read(source)
                self.assertFalse(backend.active)

        self.authority.read_mode = "bad_signature"

        self.assert_rejected_read(self.source)
        self.assertFalse(self.authority.active)

    def test_replayed_signed_read_fails_fresh_challenge(
        self
    ):
        self.assertEqual(
            self.read(),
            self.fixture.expected(),
        )

        original = self.authority.read_challenges[0]

        self.authority.read_mode = "replay"

        self.assert_rejected_read(self.source)

        self.assertEqual(
            self.authority.read_calls,
            2,
        )

        self.assertNotEqual(
            original,
            self.authority.read_challenges[1],
        )

        self.assertFalse(self.authority.active)
        self.assertEqual(self.authority.cas_calls, 0)

    def test_invalid_cas_inputs_never_dispatch(
        self
    ):
        invalid = (
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

        for changes in invalid:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.advance(**changes)

                self.assertEqual(
                    self.authority.cas_calls,
                    0,
                )

                self.assertEqual(
                    self.authority.read_calls,
                    0,
                )

        self.assertEqual(
            self.authority.revision,
            OLD,
        )

    def test_mutated_frozen_source_fails_closed(self):
        mutations = (
            ("authority", None),
            ("expected_authority_id", ""),
            ("expected_authority_public_key", b"short"),
            ("expected_root_id", True),
            ("expected_root_public_key", b"short"),
            ("expected_enrollment_epoch", True),
            ("minimum_revision", True),
            ("minimum_generation", -1),
            ("minimum_fence_token", True),
        )

        for field, replacement in mutations:
            with self.subTest(field=field):
                source = self.fixture.make_source()

                object.__setattr__(
                    source,
                    field,
                    replacement,
                )

                self.assert_rejected_read(source)

                with self.assertRaises(ValueError):
                    self.advance(source)

                self.assertEqual(
                    self.authority.cas_calls,
                    0,
                )

                self.assertEqual(
                    self.authority.read_calls,
                    0,
                )

    def test_valid_signature_with_wrong_cas_fields_rejected(
        self
    ):
        attacks = (
            ("expected_revision", OLD + 1),
            ("next_revision", NEXT + 1),
            ("expected_generation", GENERATION + 1),
            ("expected_fence_token", FENCE + 1),
            ("revision", NEXT + 1),
            ("generation", GENERATION + 2),
            ("fence_token", FENCE + 2),
            ("challenge_hex", "aa" * 32),
        )

        for field, replacement in attacks:
            with self.subTest(field=field):
                backend, source = self.injected(
                    change_field(field, replacement),
                    operation="cas",
                )

                with self.assertRaises(ValueError):
                    self.advance(source)

                # The test backend commits before signing.
                # A rejected response does NOT prove rollback.
                self.assertEqual(backend.cas_calls, 1)
                self.assertEqual(backend.revision, NEXT)
                self.assertEqual(backend.read_calls, 0)
                self.assertFalse(backend.active)

    def test_postcommit_readback_failures_do_not_retry_cas(
        self
    ):
        scenarios = (
            "wrong_challenge",
            "wrong_root",
            "bad_signature",
            "transport_failure",
            "signed_stale_revision",
        )

        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                if scenario == "signed_stale_revision":
                    backend, source = self.injected(
                        change_field("revision", OLD),
                        operation="read",
                    )

                else:
                    backend = (
                        contract.SignedMemoryMonotonicAuthority(
                            self.fixture.private
                        )
                    )

                    source = self.fixture.make_source(
                        authority=backend,
                    )

                    if scenario == "transport_failure":
                        backend.read_failure = True
                    else:
                        backend.read_mode = scenario

                with self.assertRaises(ValueError):
                    self.advance(source)

                self.assertEqual(backend.cas_calls, 1)
                self.assertEqual(backend.revision, NEXT)
                self.assertEqual(
                    backend.generation,
                    GENERATION + 1,
                )

                self.assertEqual(
                    backend.fence_token,
                    FENCE + 1,
                )

                # No retry is allowed after uncertain CAS.
                self.assertFalse(backend.active)

    def test_sequential_cas_tracks_revision_generation_fence(
        self
    ):
        first = self.advance()

        self.assertEqual(
            first,
            self.fixture.expected(
                revision=NEXT,
                generation=GENERATION + 1,
                fence_token=FENCE + 1,
            ),
        )

        second = self.advance(
            expected_revision=NEXT,
            next_revision=NEXT + 1,
            expected_generation=GENERATION + 1,
            expected_fence_token=FENCE + 1,
        )

        self.assertEqual(
            second,
            self.fixture.expected(
                revision=NEXT + 1,
                generation=GENERATION + 2,
                fence_token=FENCE + 2,
            ),
        )

        self.assertEqual(self.read(), second)
        self.assertEqual(self.authority.cas_calls, 2)

        with self.assertRaises(ValueError):
            self.advance(
                expected_revision=OLD,
                next_revision=NEXT,
                expected_generation=GENERATION,
                expected_fence_token=FENCE,
            )

        self.assertEqual(
            self.authority.revision,
            NEXT + 1,
        )

    def test_suppressed_caller_error_and_repin_limitation(
        self
    ):
        self.authority.suppress_caller_error = True

        with self.assertRaises(ValueError):
            with self.source.hold() as snapshot:
                self.assertEqual(
                    snapshot,
                    self.fixture.expected(),
                )

                raise ValueError(
                    "Injected caller verification failure."
                )

        self.assertFalse(self.authority.active)

        rogue_private = Ed25519PrivateKey.generate()

        rogue = contract.SignedMemoryMonotonicAuthority(
            rogue_private
        )

        untrusted = self.fixture.make_source(
            authority=rogue
        )

        self.assert_rejected_read(untrusted)

        # The same rogue signer passes if the caller
        # changes the key pin. This is NOT independently
        # authenticated enrollment.
        repinned = self.fixture.make_source(
            authority=rogue,
            expected_authority_public_key=(
                contract.public_bytes(rogue_private)
            ),
        )

        self.assertEqual(
            self.read(repinned),
            self.fixture.expected(),
        )

        self.assertFalse(rogue.active)

    def test_rollback_floor_reset_and_false_signed_cas_limits(
        self
    ):
        self.advance()

        self.assertEqual(
            self.authority.revision,
            NEXT,
        )

        # Simulate an untrusted authority resetting its
        # internal counters after an earlier publication.
        self.authority.revision = OLD
        self.authority.generation = GENERATION
        self.authority.fence_token = FENCE

        # The original client has only caller-controlled
        # floors and accepts the signed older state.
        self.assertEqual(
            self.read(),
            self.fixture.expected(),
        )

        stricter = self.fixture.make_source(
            minimum_revision=NEXT,
            minimum_generation=GENERATION + 1,
            minimum_fence_token=FENCE + 1,
        )

        self.assert_rejected_read(stricter)

        # Separate limitation: a malicious signer may
        # sign a fake CAS acknowledgement and fake readback
        # while retaining unchanged internal state.
        lying = contract.SignedMemoryMonotonicAuthority(
            self.fixture.private
        )

        lying.fake_ack = True
        lying.lie_readback = True

        source = self.fixture.make_source(
            authority=lying
        )

        verified_claim = self.advance(source)

        self.assertEqual(
            verified_claim,
            self.fixture.expected(
                revision=NEXT,
                generation=GENERATION + 1,
                fence_token=FENCE + 1,
            ),
        )

        self.assertEqual(lying.revision, OLD)
        self.assertEqual(lying.generation, GENERATION)
        self.assertEqual(lying.fence_token, FENCE)

        for forbidden in (
            "restore",
            "republish",
            "authorize",
            "bootstrap",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertFalse(
                    hasattr(source, forbidden)
                )


if __name__ == "__main__":
    unittest.main()
