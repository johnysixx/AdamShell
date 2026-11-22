"""A44 / 66.31B — RED contract for a signed provisioning-generation floor.

TARGET API:

PinnedSignedProvisioningGenerationClient.from_authority(
    authority,
    expected_authority_id,
    expected_authority_public_key,
    expected_subject_id,
    minimum_generation,
)

client.read_generation() -> int

client.advance_if_current(
    operation_id, expected_generation, next_generation
) -> int

client.lookup_operation(operation_id)
    -> ("committed" | "unknown", current_generation)

client.bind_provisioning(source, manifest, signature)
    -> PinnedHighWaterProvisioning

Authority protocol:
    authority.hold(challenge) -> context yielding signed pair
    authority.advance_if_current(
        operation_id, expected_generation, next_generation, challenge
    ) -> signed pair
    authority.lookup_operation(operation_id, challenge)
        -> signed pair

Canonical ASCII JSON and Ed25519 signature.
Every operation uses a fresh 32-byte challenge.

Common signed fields:
    domain, version, operation, authority_id, subject_id,
    generation, challenge_hex

CAS adds:
    operation_id, expected_generation, next_generation, status

Lookup adds:
    operation_id, status

Bootstrap requires exact equality between the signed
authoritative generation and source.pins.provisioning_generation.
It rejects both stale and uncommitted future generations.

SECURITY LIMITS:
- The provider is an in-memory simulation.
- The caller independently authenticates authority ID and public key.
- Signed responses do not prove durable storage or linearizability.
- No secure deployment, transport or key isolation is provided.
- No cross-store atomicity is claimed.
- An unknown lookup never authorizes automatic CAS retry.
"""

import importlib
import json
import sys
import threading
import unittest

from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_protected_provisioning_contract as provisioning_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_floor"
)

TYPE = "PinnedSignedProvisioningGenerationClient"

DOMAIN = "AdamShell/A44/provisioning-generation-floor/v1"

AUTHORITY_ID = "a44-provisioning-floor-authority"
SUBJECT_ID = "a44-provisioning-main"

OP_A = "a" * 32
OP_B = "b" * 32


def canonical(document):
    return json.dumps(
        document,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def public_key(private_key):
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class SimulatedSignedProvisioningFloorAuthority:
    """Protocol mock, NOT an independent durable authority."""

    def __init__(self, signer):
        self.signer = signer
        self.response_signer = signer

        self.generation = 1
        self.operations = {}

        self.cas_calls = 0
        self.lock = threading.RLock()

        self.fail_after_commit = False
        self.replay_read = None
        self.rewrite = None
        self.encoder = canonical

    def _signed(self, operation, challenge, extra=None):
        document = {
            "domain": DOMAIN,
            "version": 1,
            "operation": operation,
            "authority_id": AUTHORITY_ID,
            "subject_id": SUBJECT_ID,
            "generation": self.generation,
            "challenge_hex": challenge.hex(),
        }

        if extra:
            document.update(extra)

        if self.rewrite is not None:
            document = self.rewrite(
                operation,
                document,
            )

        payload = self.encoder(document)

        return (
            payload,
            self.response_signer.sign(payload),
        )

    @contextmanager
    def hold(self, *, challenge):
        with self.lock:
            response = (
                self.replay_read
                or self._signed("read", challenge)
            )

            yield response

    def advance_if_current(
        self,
        *,
        operation_id,
        expected_generation,
        next_generation,
        challenge,
    ):
        with self.lock:
            self.cas_calls += 1

            request = (
                expected_generation,
                next_generation,
            )

            if operation_id in self.operations:
                previous, _ = self.operations[operation_id]

                if request != previous:
                    raise ValueError(
                        "Operation ID reused for another request."
                    )

                status = "committed"

            elif expected_generation != self.generation:
                status = "rejected"

            elif next_generation != expected_generation + 1:
                raise ValueError(
                    "Non-monotonic provisioning generation."
                )

            else:
                self.generation = next_generation

                self.operations[operation_id] = (
                    request,
                    next_generation,
                )

                status = "committed"

            response = self._signed(
                "cas",
                challenge,
                {
                    "operation_id": operation_id,
                    "expected_generation": expected_generation,
                    "next_generation": next_generation,
                    "status": status,
                },
            )

            if (
                self.fail_after_commit
                and status == "committed"
            ):
                self.fail_after_commit = False

                raise TimeoutError(
                    "Simulated lost signed CAS acknowledgement."
                )

            return response

    def lookup_operation(
        self,
        *,
        operation_id,
        challenge,
    ):
        with self.lock:
            return self._signed(
                "lookup",
                challenge,
                {
                    "operation_id": operation_id,
                    "status": (
                        "committed"
                        if operation_id in self.operations
                        else "unknown"
                    ),
                },
            )


class A44ProtectedProvisioningFloorContractTests(unittest.TestCase):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.client_type = getattr(
            module,
            TYPE,
        )

        self.signer = Ed25519PrivateKey.generate()

        self.authority = (
            SimulatedSignedProvisioningFloorAuthority(
                self.signer
            )
        )

        self.fixture = (
            provisioning_contract
            .A44ProtectedProvisioningContractTests(
                "test_01_trusted_source_binds_signed_enrollment"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def client(self, **changes):
        arguments = {
            "authority": self.authority,
            "expected_authority_id": AUTHORITY_ID,
            "expected_authority_public_key": public_key(
                self.signer
            ),
            "expected_subject_id": SUBJECT_ID,
            "minimum_generation": 1,
        }

        arguments.update(changes)

        return self.client_type.from_authority(
            **arguments
        )

    def bind(
        self,
        client=None,
        *,
        manifest=None,
        signature=None,
    ):
        if client is None:
            client = self.client()

        return client.bind_provisioning(
            source=self.fixture.source,
            manifest=(
                self.fixture.manifest
                if manifest is None
                else manifest
            ),
            signature=(
                self.fixture.signature
                if signature is None
                else signature
            ),
        )

    def update_source(self):
        self.fixture.source.pins = (
            self.fixture.changed_pins(
                minimum_revision=11,
                minimum_generation=21,
                minimum_fence_token=31,
                provisioning_generation=2,
            )
        )

        manifest = self.fixture.higher_manifest()

        signature = (
            self.fixture.enrollment_fixture.signer.sign(
                manifest
            )
        )

        return manifest, signature

    def advance(self, client=None, **changes):
        if client is None:
            client = self.client()

        arguments = {
            "operation_id": OP_A,
            "expected_generation": 1,
            "next_generation": 2,
        }

        arguments.update(changes)

        return client.advance_if_current(
            **arguments
        )

    def test_01_signed_initial_generation(self):
        self.assertEqual(
            self.client().read_generation(),
            1,
        )

    def test_02_matching_signed_floor_allows_bootstrap(self):
        binding = self.bind()

        self.assertEqual(
            binding.pins.provisioning_generation,
            1,
        )

    def test_03_advanced_floor_rejects_reconstructed_old_source(self):
        self.advance()

        with self.assertRaises(ValueError):
            self.bind(
                self.client(minimum_generation=2)
            )

    def test_04_advanced_floor_allows_signed_updated_source(self):
        manifest, signature = self.update_source()

        client = self.client()

        self.assertEqual(
            self.advance(client),
            2,
        )

        binding = self.bind(
            client,
            manifest=manifest,
            signature=signature,
        )

        self.assertEqual(
            binding.pins.provisioning_generation,
            2,
        )

    def test_05_uncommitted_higher_source_generation_rejected(self):
        manifest, signature = self.update_source()

        with self.assertRaises(ValueError):
            self.bind(
                manifest=manifest,
                signature=signature,
            )

        self.assertEqual(
            self.authority.generation,
            1,
        )

    def test_06_missing_protocol_capability_rejected(self):
        with self.assertRaises(ValueError):
            self.client(
                authority=object()
            )

    def test_07_signed_authority_id_substitution_rejected(self):
        self.authority.rewrite = lambda op, doc: {
            **doc,
            "authority_id": "attacker-authority",
        }

        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_08_signed_subject_substitution_rejected(self):
        self.authority.rewrite = lambda op, doc: {
            **doc,
            "subject_id": "different-provisioning-project",
        }

        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_09_attacker_signed_response_rejected(self):
        self.authority.response_signer = (
            Ed25519PrivateKey.generate()
        )

        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_10_replayed_signed_read_rejected(self):
        client = self.client()

        self.assertEqual(
            client.read_generation(),
            1,
        )

        self.authority.replay_read = (
            self.authority._signed(
                "read",
                b"x" * 32,
            )
        )

        with self.assertRaises(ValueError):
            client.read_generation()

    def test_11_noncanonical_signed_document_rejected(self):
        self.authority.encoder = (
            lambda doc: canonical(doc) + b" "
        )

        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_12_signed_unknown_and_duplicate_fields_rejected(self):
        self.authority.rewrite = lambda op, doc: {
            **doc,
            "injected": "extra",
        }

        with self.assertRaises(ValueError):
            self.client().read_generation()

        self.authority.rewrite = None

        self.authority.encoder = lambda doc: (
            canonical(doc).replace(
                b'"version":1',
                b'"version":1,"version":1',
            )
        )

        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_13_invalid_authority_key_pins_rejected(self):
        for key in (
            b"1" * 31,
            b"1" * 33,
            bytearray(b"1" * 32),
            None,
        ):
            with self.subTest(
                key=type(key).__name__
            ):
                with self.assertRaises(ValueError):
                    self.client(
                        expected_authority_public_key=key
                    )

        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.client(
                expected_authority_public_key=public_key(
                    attacker
                )
            ).read_generation()

    def test_14_invalid_generation_and_identity_values_rejected(self):
        for value in (
            True,
            -1,
            1 << 100,
            1.1,
        ):
            with self.subTest(generation=value):
                with self.assertRaises(ValueError):
                    self.client(
                        minimum_generation=value
                    )

        for name in (
            "expected_authority_id",
            "expected_subject_id",
        ):
            with self.subTest(field=name):
                with self.assertRaises(ValueError):
                    self.client(
                        **{name: ""}
                    )

        self.authority.generation = -1

        with self.assertRaises(ValueError):
            self.client().read_generation()

    def test_15_signed_cas_advances_floor(self):
        client = self.client()

        self.assertEqual(
            self.advance(client),
            2,
        )

        self.assertEqual(
            client.read_generation(),
            2,
        )

        self.assertEqual(
            self.authority.cas_calls,
            1,
        )

    def test_16_stale_cas_rejected_without_mutation(self):
        with self.assertRaises(ValueError):
            self.advance(
                expected_generation=0,
                next_generation=1,
            )

        self.assertEqual(
            self.authority.generation,
            1,
        )

        self.assertEqual(
            self.authority.operations,
            {},
        )

    def test_17_operation_id_idempotent_but_not_reusable(self):
        client = self.client()

        self.assertEqual(
            self.advance(client),
            2,
        )

        self.assertEqual(
            self.advance(client),
            2,
        )

        with self.assertRaises(ValueError):
            self.advance(
                client,
                expected_generation=2,
                next_generation=3,
            )

        self.assertEqual(
            len(self.authority.operations),
            1,
        )

        self.assertEqual(
            client.read_generation(),
            2,
        )

    def test_18_signed_lookup_unknown_and_committed(self):
        client = self.client()

        self.assertEqual(
            client.lookup_operation(
                operation_id=OP_B
            ),
            ("unknown", 1),
        )

        self.assertEqual(
            self.advance(client),
            2,
        )

        self.assertEqual(
            client.lookup_operation(
                operation_id=OP_A
            ),
            ("committed", 2),
        )

    def test_19_lost_cas_ack_requires_lookup_no_auto_retry(self):
        client = self.client()

        self.authority.fail_after_commit = True

        with self.assertRaises(ValueError):
            self.advance(client)

        self.assertEqual(
            self.authority.cas_calls,
            1,
        )

        self.assertEqual(
            client.lookup_operation(
                operation_id=OP_A
            ),
            ("committed", 2),
        )

    def test_20_signed_rollback_below_pinned_minimum_rejected(self):
        client = self.client()

        self.assertEqual(
            self.advance(client),
            2,
        )

        upgraded = self.client(
            minimum_generation=2
        )

        self.assertEqual(
            upgraded.read_generation(),
            2,
        )

        # Simulated dishonest provider rollback.
        self.authority.generation = 1

        with self.assertRaises(ValueError):
            upgraded.read_generation()

        with self.assertRaises(ValueError):
            self.bind(upgraded)


if __name__ == "__main__":
    unittest.main()
