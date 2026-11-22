"""A44 / 66.30D provisioning trust and monotonicity adversarial tests.

All trusted-source objects are simulations, not protected services.

KNOWN LIMITS:
- Caller may substitute the entire external trusted source.
- Previous in-memory binding may remain usable after refresh.
- There is no persistent protected provisioning generation.
- There is no independent hardware or remote trust authority.
"""

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

import test_a44_checkpoint_protected_provisioning_contract as contract
import test_a44_checkpoint_protected_high_water_contract as high_water_contract
import test_a44_checkpoint_anchor_cas_backend_contract as backend_contract


class A44ProtectedProvisioningAdversarialTests(unittest.TestCase):

    def setUp(self):
        self.fixture = (
            contract.A44ProtectedProvisioningContractTests(
                "test_01_trusted_source_binds_signed_enrollment"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def bind(self, **changes):
        return self.fixture.bind(**changes)

    def pins(self, **changes):
        return self.fixture.changed_pins(**changes)

    def signed(self, changes=None, signer=None):
        payload = self.fixture.enrollment_fixture.payload(changes)

        if signer is None:
            signer = self.fixture.enrollment_fixture.signer

        return payload, signer.sign(payload)

    def elevate(self, advance_provider=False):
        old = self.bind()

        if advance_provider:
            result = self.fixture.fixture.advance(
                old.high_water_client(
                    self.fixture.fixture.provider
                )
            )
            self.assertEqual(result, (11, 21, 31))

        self.fixture.source.pins = self.pins(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
            provisioning_generation=2,
        )

        manifest, signature = self.signed({
            "minimum_revision": 11,
            "minimum_generation": 21,
            "minimum_fence_token": 31,
        })

        newer = old.refresh(
            manifest=manifest,
            signature=signature,
        )

        return old, newer

    def test_01_missing_source_reader_rejected(self):
        class Missing:
            pass

        with self.assertRaises(ValueError):
            self.bind(source=Missing())

        self.assertEqual(self.fixture.source.reads, 0)

    def test_02_source_read_failure_fails_closed(self):
        self.fixture.source.failure = RuntimeError(
            "Trusted source unavailable"
        )

        with self.assertRaises(ValueError):
            self.bind()

        self.assertEqual(self.fixture.source.reads, 1)

    def test_03_noncanonical_source_pins_rejected(self):
        for value in ({}, None, ("store", "key")):
            with self.subTest(value=type(value).__name__):
                self.fixture.source.pins = value

                with self.assertRaises(ValueError):
                    self.bind()

    def test_04_invalid_provisioning_signer_keys_rejected(self):
        for key in (
            b"\x01" * 31,
            b"\x01" * 33,
            bytearray(b"\x01" * 32),
            None,
        ):
            with self.subTest(key_type=type(key).__name__,
                              length=0 if key is None else len(key)):
                with self.assertRaises(ValueError):
                    self.pins(trusted_signer_public_key=key)

    def test_05_invalid_store_signer_keys_rejected(self):
        for key in (
            b"\x02" * 31,
            b"\x02" * 33,
            bytearray(b"\x02" * 32),
            None,
        ):
            with self.subTest(key_type=type(key).__name__,
                              length=0 if key is None else len(key)):
                with self.assertRaises(ValueError):
                    self.pins(expected_store_public_key=key)

    def test_06_invalid_identity_fields_rejected(self):
        for name in (
            "trusted_signer_id",
            "expected_anchor_id",
            "expected_authority_id",
            "expected_root_id",
            "expected_store_id",
        ):
            with self.subTest(field=name):
                with self.assertRaises(ValueError):
                    self.pins(**{name: ""})

    def test_07_invalid_counter_values_rejected(self):
        for name, value in (
            ("minimum_enrollment_epoch", True),
            ("minimum_revision", True),
            ("minimum_generation", -1),
            ("minimum_fence_token", False),
            ("provisioning_generation", -1),
            ("provisioning_generation", 1 << 100),
        ):
            with self.subTest(field=name, value=value):
                with self.assertRaises(ValueError):
                    self.pins(**{name: value})

    def test_08_provisioning_signer_identity_rejected(self):
        self.fixture.source.pins = self.pins(
            trusted_signer_id="attacker-provisioning-root"
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_09_provisioning_signer_key_substitution_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        self.fixture.source.pins = self.pins(
            trusted_signer_public_key=backend_contract.public_key(
                attacker
            )
        )

        with self.assertRaises(ValueError):
            self.bind()

    def test_10_attacker_signed_manifest_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        manifest, signature = self.signed(
            {"signer_id": "attacker-provisioning-root"},
            signer=attacker,
        )

        with self.assertRaises(ValueError):
            self.bind(
                manifest=manifest,
                signature=signature,
            )

    def test_11_signed_identity_tampering_rejected(self):
        for name in ("anchor_id", "authority_id", "root_id"):
            with self.subTest(field=name):
                manifest, signature = self.signed({
                    name: "attacker-" + name,
                })

                with self.assertRaises(ValueError):
                    self.bind(
                        manifest=manifest,
                        signature=signature,
                    )

    def test_12_stale_manifest_below_external_pins_rejected(self):
        for name, value in (
            (
                "minimum_enrollment_epoch",
                self.fixture.pins.minimum_enrollment_epoch + 1,
            ),
            ("minimum_revision", 11),
            ("minimum_generation", 21),
            ("minimum_fence_token", 31),
        ):
            with self.subTest(field=name):
                self.fixture.source.pins = self.pins(
                    **{name: value}
                )

                try:
                    with self.assertRaises(ValueError):
                        self.bind()
                finally:
                    self.fixture.source.pins = self.fixture.pins

    def test_13_store_identity_substitution_rejected(self):
        self.fixture.source.pins = self.pins(
            expected_store_id="attacker-high-water-store"
        )

        binding = self.bind()

        with self.assertRaises(ValueError):
            self.fixture.read(binding)

    def test_14_store_signing_key_substitution_rejected(self):
        attacker = Ed25519PrivateKey.generate()

        self.fixture.source.pins = self.pins(
            expected_store_public_key=backend_contract.public_key(
                attacker
            )
        )

        binding = self.bind()

        with self.assertRaises(ValueError):
            self.fixture.read(binding)

    def test_15_existing_binding_ignores_source_mutation(self):
        binding = self.bind()
        original_key = binding.pins.expected_store_public_key

        attacker = Ed25519PrivateKey.generate()

        self.fixture.source.pins = self.pins(
            expected_store_public_key=backend_contract.public_key(
                attacker
            )
        )

        self.assertEqual(
            binding.pins.expected_store_public_key,
            original_key,
        )

        self.assertEqual(
            self.fixture.read(binding),
            (10, 20, 30),
        )

        forged_provider = (
            high_water_contract.SimulatedSignedHighWaterProvider(
                enrollment=binding.enrollment,
                signer=attacker,
            )
        )

        with self.assertRaises(ValueError):
            self.fixture.read(binding, forged_provider)

    def test_16_refresh_rejects_generation_rollback(self):
        original_pins = self.fixture.pins
        old, newer = self.elevate()

        self.assertEqual(
            newer.pins.provisioning_generation,
            2,
        )

        self.fixture.source.pins = original_pins

        with self.assertRaises(ValueError):
            newer.refresh(
                manifest=self.fixture.manifest,
                signature=self.fixture.signature,
            )

        self.fixture.source.pins = self.pins(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
            provisioning_generation=1,
        )

        manifest, signature = self.signed({
            "minimum_revision": 11,
            "minimum_generation": 21,
            "minimum_fence_token": 31,
        })

        with self.assertRaises(ValueError):
            old.refresh(
                manifest=manifest,
                signature=signature,
            )

    def test_17_refresh_rejects_silent_key_rotation(self):
        old = self.bind()
        attacker = Ed25519PrivateKey.generate()
        attacker_key = backend_contract.public_key(attacker)

        manifest, signature = self.signed(
            {"signer_id": "attacker-provisioning-root"},
            signer=attacker,
        )

        self.fixture.source.pins = self.pins(
            trusted_signer_id="attacker-provisioning-root",
            trusted_signer_public_key=attacker_key,
            provisioning_generation=2,
        )

        with self.assertRaises(ValueError):
            old.refresh(
                manifest=manifest,
                signature=signature,
            )

        self.fixture.source.pins = self.pins(
            expected_store_public_key=attacker_key,
            provisioning_generation=2,
        )

        with self.assertRaises(ValueError):
            old.refresh(
                manifest=self.fixture.manifest,
                signature=self.fixture.signature,
            )

        self.assertEqual(
            self.fixture.read(old),
            (10, 20, 30),
        )

    def test_18_old_binding_rollback_known_limit(self):
        """Old in-memory pins are not externally revoked."""

        old, newer = self.elevate(
            advance_provider=True
        )

        self.assertEqual(
            self.fixture.read(newer),
            (11, 21, 31),
        )

        provider = self.fixture.fixture.provider

        # Simulated rollback of the signed provider state.
        provider.floor = (10, 20, 30)

        # Old binding accepts the previously trusted minimum.
        self.assertEqual(
            self.fixture.read(old),
            (10, 20, 30),
        )

        # Updated binding rejects the same stale response.
        with self.assertRaises(ValueError):
            self.fixture.read(newer)

        # No external revocation or durable generation
        # enforcement is provided by the Python binding.


if __name__ == "__main__":
    unittest.main()
