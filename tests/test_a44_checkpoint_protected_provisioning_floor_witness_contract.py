"""A44 / 66.33B RED: independently pinned signed-generation witness.

Target: core.existence.history_receipt_trust_checkpoint_protected_provisioning_floor_pinned_witness
Class: PinnedSignedProvisioningGenerationWitness

from_sources(*, client, witness, expected_witness_id,
             expected_witness_public_key, expected_subject_id,
             minimum_generation)
read_generation() -> int
bind_provisioning(*, source, manifest, signature) -> PinnedHighWaterProvisioning

witness.hold(challenge=32-byte random bytes) yields a pair of bytes:
canonical ASCII JSON and a detached Ed25519 signature.
The signed document contains exactly: domain, version, operation,
witness_id, subject_id, generation, challenge_hex.

This contract uses an IN-MEMORY witness. It does not establish actual
independence, rollback-proof persistence, protected keys, remote leases,
cross-store atomicity, or secure installation of caller trust pins.
"""

import importlib
import json
import shutil
import sys
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_a44_checkpoint_protected_provisioning_floor_contract as floor_contract
import test_a44_checkpoint_protected_provisioning_floor_sqlite_backend_contract as sqlite_contract

MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_provisioning_floor_pinned_witness"
)

TYPE = "PinnedSignedProvisioningGenerationWitness"
DOMAIN = "AdamShell/A44/provisioning-generation-witness/v1"
WITNESS_ID = "a44-provisioning-independent-witness"
SUBJECT_ID = sqlite_contract.SUBJECT_ID


def canonical(document):
    return json.dumps(
        document,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


def public_key(signer):
    return signer.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class SimulatedSignedGenerationWitness:
    """Untrusted local mock, NOT an independently deployed witness."""

    def __init__(self, signer):
        self.signer = signer
        self.response_signer = signer
        self.generation = 1
        self.lock = threading.RLock()
        self.holds = 0
        self.active = False
        self.replay = None
        self.response = None
        self.rewrite = None
        self.encoder = canonical
        self.fail = False

    def signed(self, challenge):
        document = dict(
            domain=DOMAIN,
            version=1,
            operation="read",
            witness_id=WITNESS_ID,
            subject_id=SUBJECT_ID,
            generation=self.generation,
            challenge_hex=challenge.hex(),
        )

        if self.rewrite is not None:
            document = self.rewrite(document)

        payload = self.encoder(document)

        return payload, self.response_signer.sign(payload)

    @contextmanager
    def hold(self, *, challenge):
        with self.lock:
            self.holds += 1
            self.active = True

            try:
                if self.fail:
                    raise TimeoutError(
                        "Simulated witness outage"
                    )

                yield (
                    self.response
                    if self.response is not None
                    else self.replay
                    if self.replay is not None
                    else self.signed(challenge)
                )

            finally:
                self.active = False


class A44ProvisioningGenerationWitnessContractTests(unittest.TestCase):

    def setUp(self):
        module = importlib.import_module(MODULE)
        self.guard_type = getattr(module, TYPE)

        self.fixture = (
            sqlite_contract
            .A44ProvisioningGenerationSQLiteBackendContractTests(
                "test_01_bootstrap_signed_initial_read"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.signer = Ed25519PrivateKey.generate()

        self.witness = SimulatedSignedGenerationWitness(
            self.signer
        )

    def guard(self, **changes):
        params = dict(
            client=self.fixture.client(),
            witness=self.witness,
            expected_witness_id=WITNESS_ID,
            expected_witness_public_key=public_key(
                self.signer
            ),
            expected_subject_id=SUBJECT_ID,
            minimum_generation=1,
        )

        params.update(changes)

        return self.guard_type.from_sources(**params)

    def provisioning(self):
        fixture = (
            floor_contract
            .A44ProtectedProvisioningFloorContractTests(
                "test_01_signed_initial_generation"
            )
        )

        fixture.setUp()
        self.addCleanup(fixture.doCleanups)

        return fixture

    def advance_both(self):
        self.assertEqual(
            self.fixture.advance(),
            2,
        )

        self.witness.generation = 2

    def test_01_matching_signed_read(self):
        self.assertEqual(
            self.guard().read_generation(),
            1,
        )

        self.assertEqual(
            self.witness.holds,
            1,
        )

    def test_02_matching_signed_bootstrap(self):
        source = self.provisioning()

        binding = self.guard().bind_provisioning(
            source=source.fixture.source,
            manifest=source.fixture.manifest,
            signature=source.fixture.signature,
        )

        self.assertEqual(
            binding.pins.provisioning_generation,
            1,
        )

    def test_03_witness_ahead_of_authority_fails_closed(self):
        self.witness.generation = 2

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_04_authority_ahead_of_witness_fails_closed(self):
        self.assertEqual(
            self.fixture.advance(),
            2,
        )

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_05_matching_advanced_generation_succeeds(self):
        self.advance_both()

        self.assertEqual(
            self.guard(
                minimum_generation=2
            ).read_generation(),
            2,
        )

    def test_06_advanced_bootstrap_requires_updated_source(self):
        source = self.provisioning()
        self.advance_both()

        guard = self.guard(
            minimum_generation=2
        )

        with self.assertRaises(ValueError):
            guard.bind_provisioning(
                source=source.fixture.source,
                manifest=source.fixture.manifest,
                signature=source.fixture.signature,
            )

        manifest, signature = source.update_source()

        binding = guard.bind_provisioning(
            source=source.fixture.source,
            manifest=manifest,
            signature=signature,
        )

        self.assertEqual(
            binding.pins.provisioning_generation,
            2,
        )

    def test_07_attacker_witness_signer_rejected(self):
        self.witness.response_signer = (
            Ed25519PrivateKey.generate()
        )

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_08_witness_identity_substitution_rejected(self):
        self.witness.rewrite = lambda d: {
            **d,
            "witness_id": "other-witness",
        }

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_09_witness_subject_substitution_rejected(self):
        self.witness.rewrite = lambda d: {
            **d,
            "subject_id": "other-subject",
        }

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_10_replayed_witness_challenge_rejected(self):
        self.witness.replay = self.witness.signed(
            b"x" * 32
        )

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_11_noncanonical_and_duplicate_json_rejected(self):
        for encoder in (
            lambda d: canonical(d) + b" ",
            lambda d: canonical(d).replace(
                b'"version":1',
                b'"version":1,"version":1',
            ),
        ):
            with self.subTest(encoder=repr(encoder)):
                self.witness.encoder = encoder

                with self.assertRaises(ValueError):
                    self.guard().read_generation()

        self.witness.encoder = canonical

    def test_12_unknown_signed_fields_rejected(self):
        self.witness.rewrite = lambda d: {
            **d,
            "unexpected": "field",
        }

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_13_malformed_signed_pair_and_outage_fail_closed(self):
        for result in (
            (),
            (b"invalid", b"invalid"),
            (None, None),
        ):
            with self.subTest(result=repr(result)):
                self.witness.response = result

                with self.assertRaises(ValueError):
                    self.guard().read_generation()

        self.witness.response = None
        self.witness.fail = True

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_14_invalid_key_pins_and_minimum_rejected(self):
        for key in (
            None,
            b"a" * 31,
            b"a" * 33,
            bytearray(b"a" * 32),
        ):
            with self.subTest(key=repr(key)):
                with self.assertRaises(ValueError):
                    self.guard(
                        expected_witness_public_key=key
                    )

        for value in (
            True,
            -1,
            1 << 100,
            "1",
        ):
            with self.subTest(minimum=value):
                with self.assertRaises(ValueError):
                    self.guard(
                        minimum_generation=value
                    )

        with self.assertRaises(ValueError):
            self.guard(
                minimum_generation=2
            ).read_generation()

    def test_15_missing_witness_and_invalid_client_rejected(self):
        for changes in (
            dict(witness=object()),
            dict(client=object()),
        ):
            with self.subTest(changes=list(changes)):
                with self.assertRaises(ValueError):
                    self.guard(**changes)

    def test_16_witness_hold_covers_local_verification(self):
        witness = self.witness
        authority = self.fixture.reopened()

        class CheckedAuthority:

            @contextmanager
            def hold(self, *, challenge):
                if not witness.active:
                    raise AssertionError(
                        "Witness hold not active during local read"
                    )

                with authority.hold(
                    challenge=challenge
                ) as response:
                    yield response

            def advance_if_current(self, **kwargs):
                return authority.advance_if_current(
                    **kwargs
                )

            def lookup_operation(self, **kwargs):
                return authority.lookup_operation(
                    **kwargs
                )

        source = self.provisioning()

        local = self.fixture.client(
            backend=CheckedAuthority()
        )

        guard = self.guard(
            client=local
        )

        self.assertEqual(
            guard.read_generation(),
            1,
        )

        binding = guard.bind_provisioning(
            source=source.fixture.source,
            manifest=source.fixture.manifest,
            signature=source.fixture.signature,
        )

        self.assertEqual(
            binding.pins.provisioning_generation,
            1,
        )

        self.assertFalse(
            self.witness.active
        )

    def test_17_old_valid_local_image_detected_by_witness(self):
        old_image = (
            Path(self.fixture.temp.name)
            / "old-valid-remote-floor.sqlite3"
        )

        shutil.copy2(
            self.fixture.path,
            old_image,
        )

        self.advance_both()

        self.assertEqual(
            self.guard(
                minimum_generation=2
            ).read_generation(),
            2,
        )

        shutil.copy2(
            old_image,
            self.fixture.path,
        )

        rolled_back = self.fixture.client(
            backend=self.fixture.reopened()
        )

        with self.assertRaises(ValueError):
            self.guard(
                client=rolled_back
            ).read_generation()

    def test_18_witness_rollback_detected_by_local_generation(self):
        self.advance_both()

        self.assertEqual(
            self.guard().read_generation(),
            2,
        )

        self.witness.generation = 1

        with self.assertRaises(ValueError):
            self.guard().read_generation()

    def test_19_same_authority_and_witness_signer_rejected(self):
        duplicate_signer = self.fixture.signer

        duplicate_witness = (
            SimulatedSignedGenerationWitness(
                duplicate_signer
            )
        )

        with self.assertRaises(ValueError):
            self.guard(
                witness=duplicate_witness,
                expected_witness_public_key=public_key(
                    duplicate_signer
                ),
            )


if __name__ == "__main__":
    unittest.main()
