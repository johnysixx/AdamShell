"""A44 detected security attacks create Cronenbergs."""

import io
import unittest

from contextlib import redirect_stdout

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from universe.universe import Universe

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackCronenbergBoundary,
    SecurityAttackDetected,
)

from test_a44_trusted_root_bootstrap import (
    MemoryTrustSource,
    signed_manifest,
    snapshot,
)


class A44SecurityAttackCronenbergTests(unittest.TestCase):

    def make_world(self):
        with redirect_stdout(io.StringIO()):
            return Universe(
                universe_id="a44_attack_cronenberg"
            )

    def boundary(self):
        world = self.make_world()
        return (
            world,
            SecurityAttackCronenbergBoundary(world),
        )

    def assert_cronenbergs(self, world, count):
        self.assertEqual(
            len(world.cronenbergs),
            count,
        )
        self.assertEqual(
            world.cronenberg_count,
            count,
        )

        events = [
            event
            for event in world.quantum_events
            if isinstance(
                event,
                CronenbergManifestedEvent,
            )
        ]

        self.assertEqual(
            len(events),
            count,
        )

        for event in events:
            self.assertEqual(
                event.source_component,
                "history_receipt_trust_attack",
            )

        for cronenberg in world.cronenbergs:
            self.assertIn(
                cronenberg,
                world.entities,
            )

    def test_valid_manifest_creates_no_cronenberg(self):
        world, boundary = self.boundary()

        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        catalog = boundary.bootstrap_manifest(
            message,
            signature,
            trusted_source=MemoryTrustSource(
                snapshot(root)
            ),
        )

        self.assertEqual(catalog.epoch, 1)
        self.assert_cronenbergs(world, 0)

    def test_forged_signature_creates_cronenberg(self):
        world, boundary = self.boundary()

        root = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, _ = signed_manifest(root, authority)

        source = MemoryTrustSource(snapshot(root))

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.bootstrap_manifest(
                    message,
                    attacker.sign(message),
                    trusted_source=source,
                )

        self.assertIs(source.active, False)
        self.assert_cronenbergs(world, 1)

    def test_tampered_manifest_creates_cronenberg(self):
        world, boundary = self.boundary()

        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        changed, _ = signed_manifest(
            root,
            attacker,
        )

        self.assertNotEqual(message, changed)

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.bootstrap_manifest(
                    changed,
                    signature,
                    trusted_source=MemoryTrustSource(
                        snapshot(root)
                    ),
                )

        self.assert_cronenbergs(world, 1)

    def test_stale_epoch_creates_cronenberg(self):
        world, boundary = self.boundary()

        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
            epoch=1,
        )

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.bootstrap_manifest(
                    message,
                    signature,
                    trusted_source=MemoryTrustSource(
                        snapshot(root, floor=1)
                    ),
                )

        self.assert_cronenbergs(world, 1)

    def test_root_mismatch_creates_cronenberg(self):
        world, boundary = self.boundary()

        root = Ed25519PrivateKey.generate()
        substitute = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, signature = signed_manifest(
            root,
            authority,
        )

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.bootstrap_manifest(
                    message,
                    signature,
                    trusted_source=MemoryTrustSource(
                        snapshot(substitute)
                    ),
                )

        self.assert_cronenbergs(world, 1)

    def test_noncanonical_manifest_creates_cronenberg(self):
        world, boundary = self.boundary()

        root = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, _ = signed_manifest(root, authority)
        changed = b" " + message

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.bootstrap_manifest(
                    changed,
                    root.sign(changed),
                    trusted_source=MemoryTrustSource(
                        snapshot(root)
                    ),
                )

        self.assert_cronenbergs(world, 1)

    def test_backend_outage_does_not_create_cronenberg(self):
        for failure in (
            OSError("offline"),
            RuntimeError("backend unavailable"),
        ):
            with self.subTest(failure=type(failure).__name__):
                world, boundary = self.boundary()

                root = Ed25519PrivateKey.generate()
                authority = Ed25519PrivateKey.generate()

                message, signature = signed_manifest(
                    root,
                    authority,
                )

                source = MemoryTrustSource(
                    snapshot(root),
                    failure=failure,
                )

                with self.assertRaises(ValueError):
                    boundary.bootstrap_manifest(
                        message,
                        signature,
                        trusted_source=source,
                    )

                self.assert_cronenbergs(world, 0)

    def test_explicit_attack_from_other_security_operation(self):
        world, boundary = self.boundary()

        def attack():
            raise SecurityAttackDetected(
                "attacker-controlled input"
            )

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.execute(
                    attack,
                    source_operation="receipt_signature",
                )

        self.assert_cronenbergs(world, 1)

        self.assertEqual(
            world.quantum_events[-1].source_operation,
            "receipt_signature",
        )

    def test_normal_failure_and_success_create_none(self):
        world, boundary = self.boundary()

        self.assertEqual(
            boundary.execute(
                lambda: "accepted",
                source_operation="security_validation",
            ),
            "accepted",
        )

        def unavailable():
            raise OSError("temporary failure")

        with self.assertRaises(OSError):
            boundary.execute(
                unavailable,
                source_operation="publication_fence",
            )

        self.assert_cronenbergs(world, 0)

    def test_each_detected_attempt_creates_one_cronenberg(self):
        world, boundary = self.boundary()

        def attack():
            raise SecurityAttackDetected(
                "blocked malicious operation"
            )

        with redirect_stdout(io.StringIO()):
            for _ in range(2):
                with self.assertRaises(SecurityAttackDetected):
                    boundary.execute(
                        attack,
                        source_operation="authority_reply",
                    )

        self.assert_cronenbergs(world, 2)

        self.assertNotEqual(
            world.cronenbergs[0].id,
            world.cronenbergs[1].id,
        )

    def test_attack_details_not_copied_into_event(self):
        world, boundary = self.boundary()

        secret = "PRIVATE-ATTACKER-DATA-NOT-FOR-LOG"

        def attack():
            raise SecurityAttackDetected(secret)

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.execute(
                    attack,
                    source_operation="publication_fence",
                )

        event = world.quantum_events[-1]

        self.assertNotIn(
            secret,
            event.error_message,
        )

        self.assert_cronenbergs(world, 1)

    def test_publication_failure_still_denies_operation(self):
        class BrokenWorld:
            def create_cronenberg_from_quantum_error(
                self,
                **kwargs,
            ):
                raise RuntimeError("publication failed")

        boundary = SecurityAttackCronenbergBoundary(
            BrokenWorld()
        )

        def attack():
            raise SecurityAttackDetected(
                "denied operation"
            )

        with self.assertRaises(ValueError):
            boundary.execute(
                attack,
                source_operation="security_validation",
            )


if __name__ == "__main__":
    unittest.main()
