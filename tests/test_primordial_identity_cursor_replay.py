import unittest
from dataclasses import FrozenInstanceError

from gods.god_memory_state import GodSharedMemory
from idea_universe import IdeaUniverse
from idea_universe.primordial_identity_cursor import (
    PrimordialIdentityCursor,
)
from multiverse import UniverseRegistry
from quantum.director_state import (
    QuantumDirectorStarCreatedEvent,
)
from universe.universe import Universe


class PrimordialIdentityCursorReplayTests(unittest.TestCase):

    def _layer(self, universe_id="replay_root"):
        universe = Universe(universe_id=universe_id)
        universe.universe_registry = UniverseRegistry()

        layer = IdeaUniverse(universe)
        layer.stellar_epoch_started = True

        return layer

    def test_cursor_is_frozen_object_state(self):
        cursor = PrimordialIdentityCursor(
            scope="replay_root:idea_universe:1"
        )

        self.assertEqual(cursor.star_serial, 0)
        self.assertEqual(cursor.nebula_serial, 0)

        with self.assertRaises(FrozenInstanceError):
            cursor.star_serial = 10

        for method in ("get", "items", "keys", "values"):
            self.assertFalse(hasattr(cursor, method))

        with self.assertRaises(TypeError):
            _ = cursor["star_serial"]

        with self.assertRaises(RuntimeError):
            _ = cursor.star_id

        with self.assertRaises(RuntimeError):
            _ = cursor.nebula_id

    def test_creations_replace_cursor_immutably(self):
        layer = self._layer()

        initial = layer.primordial_identity_cursor

        first_star = layer.create_primordial_star()
        first = layer.primordial_identity_cursor

        epoch = layer.run_primordial_stellar_epoch(
            star_count=2,
        )
        second = layer.primordial_identity_cursor

        self.assertIsNot(initial, first)
        self.assertIsNot(first, second)

        self.assertEqual(initial.star_serial, 0)
        self.assertEqual(initial.nebula_serial, 0)

        self.assertEqual(first.star_serial, 1)
        self.assertEqual(first.nebula_serial, 0)

        self.assertEqual(second.star_serial, 3)
        self.assertEqual(second.nebula_serial, 1)

        self.assertEqual(first_star.id, first.star_id)
        self.assertEqual(
            epoch.primordial_nebula.id,
            second.nebula_id,
        )

        with self.assertRaises(AttributeError):
            layer.primordial_identity_cursor = initial

    def test_resume_from_saved_boundary(self):
        source = self._layer()

        source.create_primordial_star()
        source.run_primordial_stellar_epoch(
            star_count=2,
        )

        saved = (
            source.public_state[
                "primordial_identity_cursor"
            ]
        )

        cursor = PrimordialIdentityCursor.from_mapping(
            saved
        )

        restored = self._layer()

        restored.restore_primordial_identity_cursor(
            cursor
        )

        next_star = restored.create_primordial_star()

        next_epoch = (
            restored.run_primordial_stellar_epoch(
                star_count=1,
            )
        )

        self.assertTrue(
            next_star.id.endswith(":primordial_star:4")
        )

        self.assertTrue(
            next_epoch.primordial_nebula.id.endswith(
                ":primordial_nebula:2"
            )
        )

        self.assertEqual(
            restored.primordial_identity_cursor.star_serial,
            5,
        )

        self.assertEqual(
            restored.primordial_identity_cursor.nebula_serial,
            2,
        )

        self.assertEqual(
            saved["star_serial"],
            3,
        )

        self.assertEqual(
            saved["nebula_serial"],
            1,
        )

    def test_partial_history_resume_has_no_id_collision(self):
        source = self._layer()

        original_ids = [
            source.create_primordial_star().id
            for _ in range(3)
        ]

        checkpoint = source.primordial_identity_cursor

        restored = self._layer()

        restored.restore_primordial_identity_cursor(
            checkpoint
        )

        continuation_ids = [
            restored.create_primordial_star().id
            for _ in range(2)
        ]

        self.assertEqual(
            len(set(original_ids + continuation_ids)),
            5,
        )

        self.assertEqual(
            continuation_ids,
            [
                "replay_root:idea_universe:1:primordial_star:4",
                "replay_root:idea_universe:1:primordial_star:5",
            ],
        )

        self.assertEqual(checkpoint.star_serial, 3)

    def test_memory_captures_resumed_identity(self):
        source = self._layer()
        source.create_primordial_star()

        checkpoint = source.primordial_identity_cursor

        restored = self._layer()
        restored.restore_primordial_identity_cursor(
            checkpoint
        )

        star = restored.create_primordial_star()

        memory = GodSharedMemory()

        memory.record(
            QuantumDirectorStarCreatedEvent(
                subject=star,
            )
        )

        self.assertEqual(
            memory.fact_at(0).value_for("subject.id"),
            star.id,
        )

        self.assertTrue(star.id.endswith(":2"))

    def test_rejects_foreign_scope_without_mutation(self):
        restored = self._layer("target")

        wrong = PrimordialIdentityCursor(
            scope="another:idea_universe:1",
            star_serial=20,
            nebula_serial=8,
        )

        initial = restored.primordial_identity_cursor

        with self.assertRaises(ValueError):
            restored.restore_primordial_identity_cursor(
                wrong
            )

        self.assertIs(
            restored.primordial_identity_cursor,
            initial,
        )

    def test_rejects_restore_into_populated_layer(self):
        layer = self._layer()

        layer.create_primordial_star()

        previous = layer.primordial_identity_cursor

        cursor = PrimordialIdentityCursor(
            scope=previous.scope,
            star_serial=100,
            nebula_serial=50,
        )

        with self.assertRaises(RuntimeError):
            layer.restore_primordial_identity_cursor(
                cursor
            )

        self.assertIs(
            layer.primordial_identity_cursor,
            previous,
        )

    def test_rejects_second_restore(self):
        layer = self._layer()

        checkpoint = PrimordialIdentityCursor(
            scope=layer.primordial_identity_cursor.scope,
            star_serial=4,
            nebula_serial=2,
        )

        layer.restore_primordial_identity_cursor(
            checkpoint
        )

        with self.assertRaises(RuntimeError):
            layer.restore_primordial_identity_cursor(
                checkpoint
            )

    def test_rejects_mapping_at_runtime_boundary(self):
        layer = self._layer()

        with self.assertRaises(TypeError):
            layer.restore_primordial_identity_cursor({
                "scope": layer.primordial_identity_cursor.scope,
                "star_serial": 1,
                "nebula_serial": 1,
            })

    def test_boundary_is_detached(self):
        layer = self._layer()

        layer.create_primordial_star()

        boundary = layer.public_state[
            "primordial_identity_cursor"
        ]

        boundary["star_serial"] = 999

        self.assertEqual(
            layer.primordial_identity_cursor.star_serial,
            1,
        )

        self.assertEqual(
            layer.universe.world["idea_universe"][
                "primordial_identity_cursor"
            ]["star_serial"],
            1,
        )

    def test_invalid_cursor_values_rejected(self):
        scope = "replay_root:idea_universe:1"

        for value in (-1,):
            with self.assertRaises(ValueError):
                PrimordialIdentityCursor(
                    scope=scope,
                    star_serial=value,
                )

        for value in (True, 1.5, "2", None):
            with self.assertRaises(TypeError):
                PrimordialIdentityCursor(
                    scope=scope,
                    nebula_serial=value,
                )

        with self.assertRaises(ValueError):
            PrimordialIdentityCursor(scope="")

        with self.assertRaises(TypeError):
            PrimordialIdentityCursor.from_mapping([])

        with self.assertRaises(ValueError):
            PrimordialIdentityCursor.from_mapping({
                "scope": scope,
                "star_serial": 2,
            })

    def test_failed_creation_does_not_advance_cursor(self):
        layer = self._layer()

        initial = layer.primordial_identity_cursor

        layer.stellar_epoch_started = False

        with self.assertRaises(RuntimeError):
            layer.create_primordial_star()

        self.assertIs(
            layer.primordial_identity_cursor,
            initial,
        )

        layer.stellar_epoch_started = True

        star = layer.create_primordial_star()

        self.assertTrue(
            star.id.endswith(":primordial_star:1")
        )


if __name__ == "__main__":
    unittest.main()
