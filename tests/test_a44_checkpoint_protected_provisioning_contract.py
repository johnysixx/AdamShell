"""A44 / 66.30B externally pinned high-water provisioning contract.

EXPECTED RED: history_receipt_trust_checkpoint_protected_provisioning
production module does not exist.

TARGET API:

TrustedProvisioningPins(
    trusted_signer_id,
    trusted_signer_public_key,
    expected_anchor_id,
    expected_authority_id,
    expected_root_id,
    expected_store_id,
    expected_store_public_key,
    minimum_enrollment_epoch,
    minimum_revision,
    minimum_generation,
    minimum_fence_token,
    provisioning_generation,
)

PinnedHighWaterProvisioning.from_trusted_source(
    *, source, manifest, signature
)

source.read_pins() -> TrustedProvisioningPins

binding.enrollment -> verified TrustedSignedCheckpointAnchorEnrollment
binding.pins -> immutable pinned snapshot
binding.high_water_client(provider) -> verified-pins high-water client

binding.refresh(*, manifest, signature)
    -> new immutable binding, with no trust-key rotation,
       no identity substitution, and no monotonic rollback.

All enrollment signatures are checked using the public
verification key supplied by the trusted source, never a
key taken from the manifest.

The source itself is caller supplied. This contract DOES NOT
authenticate the source or establish its independent storage.

KNOWN LIMIT: caller substitution of the entire trusted source
can substitute all keys and cannot be prevented by this
in-process Python abstraction.

No physical or remote durability, HSM, TPM, OS trust store,
external monotonic CAS or cross-store atomicity is claimed.
"""

import dataclasses
import importlib
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

import test_a44_checkpoint_protected_high_water_contract as high_water_contract
import test_a44_checkpoint_anchor_trusted_enrollment_contract as enrollment_contract
import test_a44_checkpoint_anchor_cas_backend_contract as backend_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning"
)

PINS_TYPE = "TrustedProvisioningPins"
BINDING_TYPE = "PinnedHighWaterProvisioning"


class FakeExternallyTrustedSource:
    """Trusted-source simulation, not a trusted deployment."""

    def __init__(self, pins):
        self.pins = pins
        self.reads = 0
        self.failure = None

    def read_pins(self):
        self.reads += 1

        if self.failure is not None:
            raise self.failure

        return self.pins


class A44ProtectedProvisioningContractTests(unittest.TestCase):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.pins_type = getattr(module, PINS_TYPE)
        self.binding_type = getattr(module, BINDING_TYPE)

        self.fixture = (
            high_water_contract.A44ProtectedHighWaterProtocolContractTests(
                "test_01_pinned_signed_read_accepts_initial_floor"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.enrollment_fixture = self.fixture.fixture
        enrolled = self.fixture.enrollment

        self.pins = self.pins_type(
            trusted_signer_id=enrollment_contract.SIGNER_ID,
            trusted_signer_public_key=self.enrollment_fixture.signer_key,
            expected_anchor_id=enrolled.expected_anchor_id,
            expected_authority_id=enrolled.expected_authority_id,
            expected_root_id=enrolled.expected_root_id,
            expected_store_id=high_water_contract.STORE_ID,
            expected_store_public_key=self.fixture.store_key,
            minimum_enrollment_epoch=enrolled.expected_enrollment_epoch,
            minimum_revision=10,
            minimum_generation=20,
            minimum_fence_token=30,
            provisioning_generation=1,
        )

        self.source = FakeExternallyTrustedSource(
            self.pins
        )

        self.manifest = (
            self.enrollment_fixture.payload()
        )

        self.signature = (
            self.enrollment_fixture.signer.sign(
                self.manifest
            )
        )

    def bind(self, *, source=None, manifest=None, signature=None):
        if source is None:
            source = self.source

        if manifest is None:
            manifest = self.manifest

        if signature is None:
            signature = self.signature

        return self.binding_type.from_trusted_source(
            source=source,
            manifest=manifest,
            signature=signature,
        )

    def changed_pins(self, **changes):
        return dataclasses.replace(
            self.pins,
            **changes,
        )

    def read(self, binding=None, provider=None):
        if binding is None:
            binding = self.bind()

        if provider is None:
            provider = self.fixture.provider

        with binding.high_water_client(
            provider
        ).hold_floor() as floor:
            return floor

    def higher_manifest(self):
        return self.enrollment_fixture.payload({
            "minimum_revision": 11,
            "minimum_generation": 21,
            "minimum_fence_token": 31,
        })

    def test_01_trusted_source_binds_signed_enrollment(self):
        binding = self.bind()

        self.assertEqual(
            self.read(binding),
            (10, 20, 30),
        )

        self.assertEqual(
            binding.enrollment.expected_anchor_id,
            self.pins.expected_anchor_id,
        )

    def test_02_trusted_source_is_read_explicitly(self):
        binding = self.bind()

        self.assertEqual(
            self.source.reads,
            1,
        )

        self.assertEqual(
            binding.pins,
            self.pins,
        )

        self.assertIsNot(
            binding.source,
            None,
        )

    def test_03_bound_client_supports_signed_cas(self):
        binding = self.bind()
        client = binding.high_water_client(
            self.fixture.provider
        )

        result = client.advance_if_current(
            operation_id=high_water_contract.OP_A,
            expected_revision=10,
            next_revision=11,
            expected_generation=20,
            expected_fence_token=30,
        )

        self.assertEqual(
            result,
            (11, 21, 31),
        )

        self.assertEqual(
            client.lookup_operation(
                operation_id=high_water_contract.OP_A
            ),
            ("committed", (11, 21, 31)),
        )

    def test_04_direct_binding_construction_refused(self):
        with self.assertRaises(ValueError):
            self.binding_type(
                source=self.source,
                pins=self.pins,
                enrollment=self.fixture.enrollment,
            )

    def test_05_missing_or_malformed_trusted_source_rejected(self):
        class MissingReader:
            pass

        class MappingReader:
            def read_pins(self):
                return {"store_id": high_water_contract.STORE_ID}

        for source in (
            MissingReader(),
            MappingReader(),
        ):
            with self.subTest(source=type(source).__name__):
                with self.assertRaises(ValueError):
                    self.bind(source=source)

    def test_06_invalid_enrollment_signature_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        with self.assertRaises(ValueError):
            self.bind(
                signature=attacker.sign(
                    self.manifest
                ),
            )

    def test_07_provisioning_signer_key_substitution_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        self.source.pins = self.changed_pins(
            trusted_signer_public_key=backend_contract.public_key(
                attacker
            )
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_08_store_signer_substitution_rejected(self):
        binding = self.bind()

        self.fixture.provider.response_signer = (
            Ed25519PrivateKey.generate()
        )

        with self.assertRaises(ValueError):
            self.read(binding)

    def test_09_signed_store_identity_substitution_rejected(self):
        self.source.pins = self.changed_pins(
            expected_store_id="attacker-high-water-store"
        )

        binding = self.bind()

        with self.assertRaises(ValueError):
            self.read(binding)

    def test_10_anchor_identity_substitution_rejected(self):
        self.source.pins = self.changed_pins(
            expected_anchor_id="attacker-anchor"
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_11_authority_identity_substitution_rejected(self):
        self.source.pins = self.changed_pins(
            expected_authority_id="attacker-authority"
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_12_root_identity_substitution_rejected(self):
        self.source.pins = self.changed_pins(
            expected_root_id="attacker-root"
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_13_stale_enrollment_epoch_rejected(self):
        self.source.pins = self.changed_pins(
            minimum_enrollment_epoch=(
                self.pins.minimum_enrollment_epoch + 1
            )
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_14_stale_enrollment_revision_rejected(self):
        self.source.pins = self.changed_pins(
            minimum_revision=11
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_15_stale_enrollment_generation_rejected(self):
        self.source.pins = self.changed_pins(
            minimum_generation=21
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_16_stale_enrollment_fence_rejected(self):
        self.source.pins = self.changed_pins(
            minimum_fence_token=31
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_17_monotonic_refresh_creates_new_binding(self):
        old = self.bind()

        self.assertEqual(
            self.fixture.advance(
                old.high_water_client(
                    self.fixture.provider
                )
            ),
            (11, 21, 31),
        )

        self.source.pins = self.changed_pins(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
            provisioning_generation=2,
        )

        manifest = self.higher_manifest()
        signature = self.enrollment_fixture.signer.sign(
            manifest
        )

        updated = old.refresh(
            manifest=manifest,
            signature=signature,
        )

        self.assertIsNot(
            updated,
            old,
        )

        self.assertEqual(
            (
                updated.pins.minimum_revision,
                updated.pins.minimum_generation,
                updated.pins.minimum_fence_token,
            ),
            (11, 21, 31),
        )

        self.assertEqual(
            (
                old.pins.minimum_revision,
                old.pins.minimum_generation,
                old.pins.minimum_fence_token,
            ),
            (10, 20, 30),
        )

        self.assertEqual(
            self.read(updated),
            (11, 21, 31),
        )

    def test_18_trusted_source_rollback_after_refresh_rejected(self):
        old = self.bind()

        self.source.pins = self.changed_pins(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
            provisioning_generation=2,
        )

        manifest = self.higher_manifest()

        updated = old.refresh(
            manifest=manifest,
            signature=self.enrollment_fixture.signer.sign(
                manifest
            ),
        )

        self.source.pins = self.pins

        with self.assertRaises(ValueError):
            updated.refresh(
                manifest=self.manifest,
                signature=self.signature,
            )

    def test_19_trusted_store_key_rotation_is_not_silent(self):
        old = self.bind()
        attacker = Ed25519PrivateKey.generate()

        self.source.pins = self.changed_pins(
            expected_store_public_key=backend_contract.public_key(
                attacker
            ),
            provisioning_generation=2,
        )

        with self.assertRaises(ValueError):
            old.refresh(
                manifest=self.manifest,
                signature=self.signature,
            )

        self.assertEqual(
            self.read(old),
            (10, 20, 30),
        )

    def test_20_entire_trust_source_substitution_is_known_limit(self):
        """KNOWN LIMIT: arbitrary caller-supplied source is not trusted."""

        attacker = Ed25519PrivateKey.generate()
        attacker_key = backend_contract.public_key(
            attacker
        )

        attacker_id = "attacker-provisioning-root"

        replaced = FakeExternallyTrustedSource(
            self.changed_pins(
                trusted_signer_id=attacker_id,
                trusted_signer_public_key=attacker_key,
                expected_store_public_key=attacker_key,
            )
        )

        attacker_manifest = self.enrollment_fixture.payload({
            "signer_id": attacker_id,
        })

        binding = self.bind(
            source=replaced,
            manifest=attacker_manifest,
            signature=attacker.sign(
                attacker_manifest
            ),
        )

        provider = (
            high_water_contract.SimulatedSignedHighWaterProvider(
                enrollment=binding.enrollment,
                signer=attacker,
            )
        )

        self.assertEqual(
            self.read(binding, provider),
            (10, 20, 30),
        )

        # A forged trusted source is indistinguishable here
        # from legitimate external trust provisioning.
        # An OS, HSM or remote service security boundary
        # must enforce who controls the trusted source.


if __name__ == "__main__":
    unittest.main()
