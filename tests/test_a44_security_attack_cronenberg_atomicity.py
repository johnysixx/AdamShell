"""A44 security-attack Cronenberg publication atomicity.

Failures are injected AFTER a registry append. A failed
publication must restore canonical world state and
must not turn the rejected security operation into success.

The test Universe is local and does not represent a
durable remote security incident or authorization service.
"""

import io
import random
import unittest

from contextlib import redirect_stdout
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from meeting_place.glass_shelf import GlassShelf
from meeting_place.bar_entity_policy import BarEntityPolicy

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


class FailOnceAppend(list):
    """Mutate the registry, then fail exactly once."""

    def __init__(self, values=()):
        super().__init__(values)
        self.armed = True

    def append(self, value):
        super().append(value)

        if self.armed:
            self.armed = False
            raise RuntimeError(
                "A44 injected partial publication"
            )


class AlwaysFailAppend(list):
    """Mutate and always fail before commit."""

    def append(self, value):
        super().append(value)
        raise RuntimeError(
            "A44 persistently unavailable publication"
        )


class A44SecurityAttackCronenbergAtomicityTests(
    unittest.TestCase
):

    @staticmethod
    def make_world():
        with redirect_stdout(io.StringIO()):
            world = Universe(
                universe_id="a44_security_atomicity"
            )

        boundary = SecurityAttackCronenbergBoundary(
            world
        )

        return world, boundary

    @staticmethod
    def blocked_attack():
        raise SecurityAttackDetected(
            "untrusted attacker payload"
        )

    @staticmethod
    def fingerprint(world, shelf=None):
        glass = None

        if shelf is not None:
            glass = (
                id(shelf.shared_glasses),
                tuple(shelf.shared_glasses),
                id(shelf.reserved_glasses),
                tuple(shelf.reserved_glasses),
                id(shelf.personal_glasses),
                dict(shelf.personal_glasses),
            )

        return (
            id(world.cronenbergs),
            tuple(world.cronenbergs),
            id(world.entities),
            tuple(world.entities),
            id(world.quantum_events),
            tuple(world.quantum_events),
            world.cronenberg_count,
            world.energy_pool,
            world.quantum_state.tick_count,
            id(world.statistics),
            tuple(
                sorted(
                    (key, id(value))
                    for key, value in world.world.items()
                )
            ),
            glass,
            random.getstate(),
        )

    def assert_one_manifestation(
        self,
        world,
        *,
        operation="security_validation",
    ):
        self.assertEqual(len(world.cronenbergs), 1)
        self.assertEqual(world.cronenberg_count, 1)
        self.assertEqual(len(world.entities), 1)
        self.assertEqual(len(world.quantum_events), 1)

        cronenberg = world.cronenbergs[0]
        event = world.quantum_events[0]

        self.assertIs(
            world.entities[0],
            cronenberg,
        )

        self.assertIsInstance(
            event,
            CronenbergManifestedEvent,
        )

        self.assertEqual(
            event.cronenberg_id,
            cronenberg.id,
        )

        self.assertEqual(
            event.source_component,
            "history_receipt_trust_attack",
        )

        self.assertEqual(
            event.source_operation,
            operation,
        )

        self.assertEqual(
            event.error_message,
            "A44 blocked security attack.",
        )

        self.assertNotIn(
            "untrusted attacker payload",
            event.error_message,
        )

    def check_failed_publication_and_retry(
        self,
        registry_name,
    ):
        world, boundary = self.make_world()

        original = getattr(world, registry_name)

        injected = FailOnceAppend(original)

        setattr(
            world,
            registry_name,
            injected,
        )

        before = self.fingerprint(world)

        with redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(
                ValueError,
                "Cronenberg publication failed",
            ):
                boundary.execute(
                    self.blocked_attack,
                    source_operation="security_validation",
                )

        self.assertIs(
            getattr(world, registry_name),
            injected,
        )

        self.assertEqual(
            self.fingerprint(world),
            before,
            "Failed publication leaked state.",
        )

        self.assertEqual(len(world.cronenbergs), 0)
        self.assertEqual(len(world.entities), 0)
        self.assertEqual(len(world.quantum_events), 0)

        # A successful retry must not duplicate the
        # partially published first Cronenberg.
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.execute(
                    self.blocked_attack,
                    source_operation="security_validation",
                )

        self.assert_one_manifestation(world)

    def test_cronenberg_registry_failure_rolls_back(self):
        self.check_failed_publication_and_retry(
            "cronenbergs"
        )

    def test_entity_registry_failure_rolls_back(self):
        self.check_failed_publication_and_retry(
            "entities"
        )

    def test_event_registry_failure_rolls_back(self):
        self.check_failed_publication_and_retry(
            "quantum_events"
        )

    def test_bar_glasses_roll_back_after_event_failure(self):
        world, boundary = self.make_world()

        with redirect_stdout(io.StringIO()):
            shelf = GlassShelf()

        world.meeting_place = SimpleNamespace(
            glass_shelf=shelf,
            bar_entity_policy=BarEntityPolicy(),
        )

        injected = FailOnceAppend(
            world.quantum_events
        )

        world.quantum_events = injected

        before = self.fingerprint(world, shelf)

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):
                boundary.execute(
                    self.blocked_attack,
                    source_operation="security_validation",
                )

        self.assertEqual(
            self.fingerprint(world, shelf),
            before,
            "Failed attack publication leaked bar state.",
        )

        self.assertEqual(len(shelf.shared_glasses), 0)
        self.assertEqual(len(shelf.reserved_glasses), 0)
        self.assertEqual(len(shelf.personal_glasses), 0)

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.execute(
                    self.blocked_attack,
                    source_operation="security_validation",
                )

        self.assert_one_manifestation(world)

    def test_forged_manifest_failure_rolls_back(self):
        world, boundary = self.make_world()

        root = Ed25519PrivateKey.generate()
        attacker = Ed25519PrivateKey.generate()
        authority = Ed25519PrivateKey.generate()

        message, _ = signed_manifest(
            root,
            authority,
        )

        forged_signature = attacker.sign(message)

        source = MemoryTrustSource(snapshot(root))

        world.quantum_events = FailOnceAppend(
            world.quantum_events
        )

        before = self.fingerprint(world)

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):
                boundary.bootstrap_manifest(
                    message,
                    forged_signature,
                    trusted_source=source,
                )

        self.assertEqual(
            self.fingerprint(world),
            before,
        )

        self.assertIs(source.active, False)
        self.assertEqual(
            source.events,
            ["enter", "exit"],
        )

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(SecurityAttackDetected):
                boundary.bootstrap_manifest(
                    message,
                    forged_signature,
                    trusted_source=source,
                )

        self.assert_one_manifestation(
            world,
            operation="signed_manifest_bootstrap",
        )

        self.assertIs(source.active, False)

    def test_repeated_attempts_after_recovery_are_distinct(self):
        world, boundary = self.make_world()

        world.entities = FailOnceAppend(
            world.entities
        )

        with redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):
                boundary.execute(
                    self.blocked_attack,
                    source_operation="receipt_signature",
                )

        self.assertEqual(len(world.cronenbergs), 0)

        with redirect_stdout(io.StringIO()):
            for _ in range(2):
                with self.assertRaises(SecurityAttackDetected):
                    boundary.execute(
                        self.blocked_attack,
                        source_operation="receipt_signature",
                    )

        self.assertEqual(len(world.cronenbergs), 2)
        self.assertEqual(world.cronenberg_count, 2)
        self.assertEqual(len(world.entities), 2)
        self.assertEqual(len(world.quantum_events), 2)

        first, second = world.cronenbergs

        self.assertNotEqual(first.id, second.id)

        self.assertEqual(
            {
                event.cronenberg_id
                for event in world.quantum_events
            },
            {first.id, second.id},
        )

        self.assertTrue(
            all(
                event.source_operation == "receipt_signature"
                for event in world.quantum_events
            )
        )

    def test_persistent_publication_failure_never_authorizes(self):
        world, boundary = self.make_world()

        world.quantum_events = AlwaysFailAppend(
            world.quantum_events
        )

        before = self.fingerprint(world)

        for _ in range(2):
            with redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(
                    ValueError,
                    "Cronenberg publication failed",
                ):
                    boundary.execute(
                        self.blocked_attack,
                        source_operation="publication_fence",
                    )

            self.assertEqual(
                self.fingerprint(world),
                before,
            )

            self.assertEqual(world.cronenberg_count, 0)

        # The attack was denied both times even though
        # no Cronenberg could be committed.
        # A future independent incident outbox is needed
        # if every attempt must survive backend failures.


if __name__ == "__main__":
    unittest.main()
