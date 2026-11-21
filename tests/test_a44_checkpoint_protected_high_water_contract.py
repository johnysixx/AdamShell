"""A44 / 66.28B protected high-water signed-provider protocol contract.

EXPECTED RED: production client module does not exist yet.

Proposed API:

    PinnedSignedProtectedHighWaterClient.from_provider(
        provider=provider,
        enrollment=verified_enrollment,
        expected_store_id=independently_pinned_id,
        expected_store_public_key=independently_pinned_ed25519_key,
        minimum_revision=trusted_floor_revision,
        minimum_generation=trusted_floor_generation,
        minimum_fence_token=trusted_floor_fence,
    )

    client.hold_floor()
        -> context manager yielding (revision, generation, fence_token)

    client.advance_if_current(
        operation_id, expected_revision, next_revision,
        expected_generation, expected_fence_token
    ) -> committed floor tuple

    client.lookup_operation(operation_id)
        -> ("committed"|"unknown", current floor tuple)

Provider returns canonical signed ASCII JSON with exact fields:

domain="AdamShell/A44/protected-high-water/v1"
version=1
operation="read"|"cas"|"lookup"
store_id
anchor_id, anchor_public_key_hex
authority_id, authority_public_key_hex
root_id, root_public_key_hex
enrollment_epoch
revision, generation, fence_token
challenge_hex

CAS adds:
operation_id, expected_revision, next_revision,
expected_generation, expected_fence_token, status.

Lookup adds:
operation_id, status.

Provider capabilities are hold, advance_if_current,
and lookup_operation. All return canonical signed response
pairs; hold is a context manager.

TRUST LIMITS:
- The test provider is an in-memory simulation.
- The store signing key is independently pinned by the caller.
- Caller control of trusted pins is not protected provisioning.
- No independent physical durability or rollback protection.
- No remote lease or authenticated transport.
- No cross-store atomicity, checkpoint restore or republication.
"""

import importlib
import json
import sys
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent),
)

import test_a44_checkpoint_anchor_trusted_enrollment_contract as enrollment_contract
import test_a44_checkpoint_anchor_cas_backend_contract as backend_contract


MODULE = (
    "core.existence."
    "history_receipt_trust_checkpoint_protected_high_water"
)

TYPE = "PinnedSignedProtectedHighWaterClient"

DOMAIN = "AdamShell/A44/protected-high-water/v1"
STORE_ID = "a44-test-independent-high-water"

OP_A = "a" * 32
OP_B = "b" * 32
OP_C = "c" * 32
OP_D = "d" * 32


def canonical(value):
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("ascii")


class SimulatedSignedHighWaterProvider:
    """Protocol mock, NOT a durable protected authority."""

    def __init__(self, *, enrollment, signer):
        self.enrollment = enrollment
        self.signer = signer
        self.store_id = STORE_ID

        self.floor = (10, 20, 30)
        self.operations = {}

        self.lock = threading.RLock()
        self.cas_calls = 0
        self.fail_after_commit = False

        self.rewrite = None
        self.encoder = canonical
        self.response_signer = signer

    def _signed(self, operation, challenge, floor, extra=None):
        document = {
            "domain": DOMAIN,
            "version": 1,
            "operation": operation,
            "store_id": self.store_id,
            "anchor_id": self.enrollment.expected_anchor_id,
            "anchor_public_key_hex": (
                self.enrollment.expected_anchor_public_key.hex()
            ),
            "authority_id": self.enrollment.expected_authority_id,
            "authority_public_key_hex": (
                self.enrollment.expected_authority_public_key.hex()
            ),
            "root_id": self.enrollment.expected_root_id,
            "root_public_key_hex": (
                self.enrollment.expected_root_public_key.hex()
            ),
            "enrollment_epoch": (
                self.enrollment.expected_enrollment_epoch
            ),
            "revision": floor[0],
            "generation": floor[1],
            "fence_token": floor[2],
            "challenge_hex": challenge.hex(),
        }

        if extra:
            document.update(extra)

        if self.rewrite is not None:
            document = self.rewrite(operation, document)

        payload = self.encoder(document)

        return (
            payload,
            self.response_signer.sign(payload),
        )

    @contextmanager
    def hold(self, *, challenge):
        with self.lock:
            response = self._signed(
                "read",
                challenge,
                self.floor,
            )

        yield response

    def advance_if_current(
        self,
        *,
        operation_id,
        expected_revision,
        next_revision,
        expected_generation,
        expected_fence_token,
        challenge,
    ):
        with self.lock:
            self.cas_calls += 1

            request = (
                expected_revision,
                next_revision,
                expected_generation,
                expected_fence_token,
            )

            if operation_id in self.operations:
                saved_request, saved_floor = (
                    self.operations[operation_id]
                )

                if saved_request != request:
                    raise ValueError(
                        "Operation ID bound to another request."
                    )

                status = "committed"
                response_floor = saved_floor

            elif (
                expected_revision,
                expected_generation,
                expected_fence_token,
            ) != self.floor:
                status = "rejected"
                response_floor = self.floor

            else:
                if next_revision <= expected_revision:
                    raise ValueError(
                        "Non-monotonic revision request."
                    )

                response_floor = (
                    next_revision,
                    expected_generation + 1,
                    expected_fence_token + 1,
                )

                self.floor = response_floor

                self.operations[operation_id] = (
                    request,
                    response_floor,
                )

                status = "committed"

            response = self._signed(
                "cas",
                challenge,
                response_floor,
                {
                    "operation_id": operation_id,
                    "expected_revision": expected_revision,
                    "next_revision": next_revision,
                    "expected_generation": expected_generation,
                    "expected_fence_token": expected_fence_token,
                    "status": status,
                },
            )

            if (
                self.fail_after_commit
                and status == "committed"
            ):
                self.fail_after_commit = False

                raise TimeoutError(
                    "Simulated lost CAS acknowledgement."
                )

            return response

    def lookup_operation(self, *, operation_id, challenge):
        with self.lock:
            status = (
                "committed"
                if operation_id in self.operations
                else "unknown"
            )

            return self._signed(
                "lookup",
                challenge,
                self.floor,
                {
                    "operation_id": operation_id,
                    "status": status,
                },
            )


class A44ProtectedHighWaterProtocolContractTests(
    unittest.TestCase
):

    def setUp(self):
        module = importlib.import_module(MODULE)

        self.client_type = getattr(
            module,
            TYPE,
        )

        self.fixture = (
            enrollment_contract.A44CheckpointAnchorTrustedEnrollmentContractTests(
                "test_01_signed_enrollment_binds_read_and_cas"
            )
        )

        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

        self.enrollment = self.fixture.enrolled()

        self.store_signer = Ed25519PrivateKey.generate()

        self.store_key = backend_contract.public_key(
            self.store_signer
        )

        self.provider = SimulatedSignedHighWaterProvider(
            enrollment=self.enrollment,
            signer=self.store_signer,
        )

    def client(self, **changes):
        arguments = {
            "provider": self.provider,
            "enrollment": self.enrollment,
            "expected_store_id": STORE_ID,
            "expected_store_public_key": self.store_key,
            "minimum_revision": 10,
            "minimum_generation": 20,
            "minimum_fence_token": 30,
        }

        arguments.update(changes)

        return self.client_type.from_provider(
            **arguments
        )

    def read(self, client=None):
        if client is None:
            client = self.client()

        with client.hold_floor() as floor:
            return floor

    def advance(
        self,
        client=None,
        *,
        operation_id=OP_A,
        expected_revision=10,
        next_revision=11,
        expected_generation=20,
        expected_fence_token=30,
    ):
        if client is None:
            client = self.client()

        return client.advance_if_current(
            operation_id=operation_id,
            expected_revision=expected_revision,
            next_revision=next_revision,
            expected_generation=expected_generation,
            expected_fence_token=expected_fence_token,
        )

    def test_01_pinned_signed_read_accepts_initial_floor(self):
        self.assertEqual(
            self.read(),
            (10, 20, 30),
        )

    def test_02_signed_cas_and_lookup_are_consistent(self):
        client = self.client()

        self.assertEqual(
            self.advance(client),
            (11, 21, 31),
        )

        self.assertEqual(
            client.lookup_operation(operation_id=OP_A),
            ("committed", (11, 21, 31)),
        )

        self.assertEqual(
            self.read(client),
            (11, 21, 31),
        )

    def test_03_repeated_operation_id_is_idempotent(self):
        client = self.client()

        self.assertEqual(
            self.advance(client),
            (11, 21, 31),
        )

        self.assertEqual(
            self.advance(client),
            (11, 21, 31),
        )

        self.assertEqual(
            len(self.provider.operations),
            1,
        )

    def test_04_historical_idempotence_does_not_rewind_floor(self):
        client = self.client()

        self.assertEqual(
            self.advance(client),
            (11, 21, 31),
        )

        self.assertEqual(
            self.advance(
                client,
                operation_id=OP_B,
                expected_revision=11,
                next_revision=12,
                expected_generation=21,
                expected_fence_token=31,
            ),
            (12, 22, 32),
        )

        self.assertEqual(
            self.advance(client),
            (11, 21, 31),
        )

        self.assertEqual(
            self.read(client),
            (12, 22, 32),
        )

        self.assertEqual(
            client.lookup_operation(operation_id=OP_A),
            ("committed", (12, 22, 32)),
        )

    def test_05_unknown_lookup_is_non_mutating(self):
        self.assertEqual(
            self.client().lookup_operation(
                operation_id=OP_C
            ),
            ("unknown", (10, 20, 30)),
        )

        self.assertEqual(
            len(self.provider.operations),
            0,
        )

    def test_06_lost_ack_does_not_auto_retry_and_lookup_recovers(self):
        client = self.client()
        self.provider.fail_after_commit = True

        with self.assertRaises(ValueError):
            self.advance(client)

        self.assertEqual(
            self.provider.cas_calls,
            1,
        )

        self.assertEqual(
            client.lookup_operation(operation_id=OP_A),
            ("committed", (11, 21, 31)),
        )

        self.assertEqual(
            self.advance(client),
            (11, 21, 31),
        )

        self.assertEqual(
            len(self.provider.operations),
            1,
        )

    def test_07_competing_distinct_cas_has_single_winner(self):
        client = self.client()

        def attempt(operation_id):
            try:
                return self.advance(
                    client,
                    operation_id=operation_id,
                )

            except ValueError:
                return None

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(
                executor.map(
                    attempt,
                    (OP_A, OP_B, OP_C, OP_D),
                )
            )

        self.assertEqual(
            results.count((11, 21, 31)),
            1,
        )

        self.assertEqual(
            len(self.provider.operations),
            1,
        )

        self.assertEqual(
            self.read(client),
            (11, 21, 31),
        )

    def test_08_competing_identical_cas_is_idempotent(self):
        client = self.client()

        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(
                executor.map(
                    lambda _: self.advance(client),
                    range(3),
                )
            )

        self.assertEqual(
            results,
            [(11, 21, 31)] * 3,
        )

        self.assertEqual(
            len(self.provider.operations),
            1,
        )

    def test_09_stale_cas_is_rejected_and_not_recorded(self):
        self.assertEqual(
            self.advance(),
            (11, 21, 31),
        )

        with self.assertRaises(ValueError):
            self.advance(operation_id=OP_B)

        self.assertNotIn(
            OP_B,
            self.provider.operations,
        )

        self.assertEqual(
            self.read(),
            (11, 21, 31),
        )

    def test_10_same_operation_id_cannot_bind_new_request(self):
        self.assertEqual(
            self.advance(),
            (11, 21, 31),
        )

        with self.assertRaises(ValueError):
            self.advance(next_revision=12)

        self.assertEqual(
            len(self.provider.operations),
            1,
        )

    def test_11_untrusted_signer_key_is_rejected(self):
        wrong = backend_contract.public_key(
            Ed25519PrivateKey.generate()
        )

        with self.assertRaises(ValueError):
            self.read(
                self.client(
                    expected_store_public_key=wrong,
                )
            )

    def test_12_wrong_signed_store_identity_is_rejected(self):
        self.provider.store_id = "attacker-store"

        with self.assertRaises(ValueError):
            self.read()

    def test_13_wrong_signed_anchor_identity_or_key_is_rejected(self):
        for key, bad in (
            ("anchor_id", "attacker-anchor"),
            ("anchor_public_key_hex", "01" * 32),
        ):
            with self.subTest(field=key):
                self.provider.rewrite = (
                    lambda op, data: {
                        **data,
                        key: bad,
                    }
                )

                with self.assertRaises(ValueError):
                    self.read()

        self.provider.rewrite = None

    def test_14_wrong_signed_authority_or_root_binding_is_rejected(self):
        for key, bad in (
            ("authority_id", "attacker-authority"),
            ("authority_public_key_hex", "02" * 32),
            ("root_id", "attacker-root"),
            ("root_public_key_hex", "03" * 32),
        ):
            with self.subTest(field=key):
                self.provider.rewrite = (
                    lambda op, data: {
                        **data,
                        key: bad,
                    }
                )

                with self.assertRaises(ValueError):
                    self.read()

        self.provider.rewrite = None

    def test_15_wrong_signed_enrollment_epoch_is_rejected(self):
        self.provider.rewrite = (
            lambda op, data: {
                **data,
                "enrollment_epoch": 4,
            }
        )

        with self.assertRaises(ValueError):
            self.read()

    def test_16_forged_or_replayed_challenge_is_rejected(self):
        self.provider.rewrite = (
            lambda op, data: {
                **data,
                "challenge_hex": (b"\x99" * 32).hex(),
            }
        )

        with self.assertRaises(ValueError):
            self.read()

        with self.assertRaises(ValueError):
            self.advance()

        self.provider.rewrite = None

    def test_17_noncanonical_duplicate_or_nonfinite_signed_data_rejected(self):
        encoders = (
            lambda d: json.dumps(
                d,
                sort_keys=True,
                indent=2,
            ).encode("ascii"),
            lambda d: b'{"version":1,' + canonical(d)[1:],
            lambda d: canonical(d).replace(
                b'"revision":10',
                b'"revision":NaN',
            ),
        )

        for i, encoder in enumerate(encoders):
            with self.subTest(case=i):
                self.provider.encoder = encoder

                with self.assertRaises(ValueError):
                    self.read()

        self.provider.encoder = canonical

    def test_18_invalid_operation_id_or_counter_inputs_rejected(self):
        for changes in (
            {"operation_id": "not-an-id"},
            {"expected_revision": True},
            {"expected_generation": -1},
            {"expected_fence_token": False},
            {"next_revision": 10},
        ):
            with self.subTest(request=changes):
                with self.assertRaises(ValueError):
                    self.advance(**changes)

        self.assertEqual(
            len(self.provider.operations),
            0,
        )

    def test_19_external_high_water_floor_rejects_rollback(self):
        client = self.client()

        self.assertEqual(
            self.advance(client),
            (11, 21, 31),
        )

        higher = self.client(
            minimum_revision=11,
            minimum_generation=21,
            minimum_fence_token=31,
        )

        self.assertEqual(
            self.read(higher),
            (11, 21, 31),
        )

        self.provider.floor = (10, 20, 30)
        self.provider.operations.clear()

        with self.assertRaises(ValueError):
            self.read(higher)

        with self.assertRaises(ValueError):
            higher.lookup_operation(
                operation_id=OP_A
            )

    def test_20_old_client_floor_accepts_rolled_back_mock_known_limit(self):
        old = self.client()

        self.assertEqual(
            self.advance(old),
            (11, 21, 31),
        )

        self.provider.floor = (10, 20, 30)
        self.provider.operations.clear()

        self.assertEqual(
            self.read(old),
            (10, 20, 30),
        )

        self.assertEqual(
            old.lookup_operation(operation_id=OP_A),
            ("unknown", (10, 20, 30)),
        )

        with self.assertRaises(ValueError):
            self.read(
                self.client(
                    minimum_revision=11,
                    minimum_generation=21,
                    minimum_fence_token=31,
                )
            )


if __name__ == "__main__":
    unittest.main()
