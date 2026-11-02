import unittest
from dataclasses import FrozenInstanceError

from gods.god_memory_state import GodSharedMemory
from idea_universe import IdeaUniverse
from idea_universe.primordial_creation_history import (
    PrimordialCreationHistory,
    PrimordialNebulaCreated,
    PrimordialRemnantCreation,
    PrimordialStarCreated,
    PrimordialStarTransition,
)
from idea_universe.primordial_idea_star_state import (
    PrimordialIdeaStarState,
)
from multiverse import UniverseRegistry
from quantum.director_state import (
    QuantumDirectorNebulaCreatedEvent,
    QuantumDirectorStarCreatedEvent,
)
from universe.universe import Universe


class PrimordialCreationHistoryReplayTests(unittest.TestCase):

    def _layer(self, universe_id="creation_replay"):
        universe = Universe(universe_id=universe_id)
        universe.universe_registry = UniverseRegistry()

        layer = IdeaUniverse(universe)
        layer.stellar_epoch_started = True

        return layer

    def test_creation_history_uses_immutable_events(self):
        layer = self._layer()

        initial = layer.primordial_creation_history

        star = layer.create_primordial_star()

        updated = layer.primordial_creation_history

        self.assertIsNot(initial, updated)
        self.assertEqual(initial.events, ())
        self.assertEqual(len(updated.events), 1)
        self.assertIsInstance(
            updated.events[0],
            PrimordialStarCreated,
        )
        self.assertEqual(
            updated.events[0].object_id,
            star.id,
        )

        with self.assertRaises(FrozenInstanceError):
            updated.events = ()

        for method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(hasattr(updated, method))

    def test_stellar_epoch_records_creation_and_transitions(self):
        layer = self._layer()

        result = layer.run_primordial_stellar_epoch(
            star_count=2,
        )

        events = layer.primordial_creation_history.events

        self.assertEqual(len(events), 7)

        self.assertIsInstance(
            events[0],
            PrimordialStarCreated,
        )
        self.assertIsInstance(
            events[1],
            PrimordialStarTransition,
        )
        self.assertIsInstance(
            events[2],
            PrimordialStarTransition,
        )
        self.assertIsInstance(
            events[-1],
            PrimordialNebulaCreated,
        )

        self.assertIs(
            events[1].state,
            PrimordialIdeaStarState.BURNING,
        )

        self.assertIs(
            events[2].state,
            PrimordialIdeaStarState.EXPLODED,
        )

        self.assertEqual(
            events[-1].object_id,
            result.primordial_nebula.id,
        )
        self.assertEqual(
            len(events[-1].remnants),
            2,
        )

    def test_replay_restores_object_ids_and_initial_states(self):
        source = self._layer()

        untouched = source.create_primordial_star()

        epoch = source.run_primordial_stellar_epoch(
            star_count=2,
        )

        history = source.primordial_creation_history
        checkpoint = source.primordial_identity_cursor

        restored = self._layer()

        rebuilt_stars, rebuilt_nebula = (
            restored.replay_primordial_creation_history(
                history
            )
        )

        self.assertEqual(
            tuple(star.id for star in rebuilt_stars),
            tuple(star.id for star in source.starry_sky),
        )

        self.assertIs(
            rebuilt_stars[0].state,
            PrimordialIdeaStarState.CREATED,
        )

        self.assertIs(
            rebuilt_stars[1].state,
            PrimordialIdeaStarState.EXPLODED,
        )

        self.assertIs(
            rebuilt_stars[2].state,
            PrimordialIdeaStarState.EXPLODED,
        )

        self.assertIsNot(
            rebuilt_stars[0],
            untouched,
        )

        self.assertEqual(
            rebuilt_nebula.id,
            epoch.primordial_nebula.id,
        )

        self.assertEqual(
            rebuilt_nebula.elemental_potentials,
            epoch.primordial_nebula.elemental_potentials,
        )

        self.assertEqual(
            restored.primordial_identity_cursor,
            checkpoint,
        )

        self.assertIs(
            restored.universe.world["idea_universe"][
                "primordial_nebula"
            ],
            rebuilt_nebula,
        )

    def test_replay_continues_without_duplicate_ids(self):
        source = self._layer()

        source.run_primordial_stellar_epoch(
            star_count=3,
        )

        history = source.primordial_creation_history

        restored = self._layer()
        restored.replay_primordial_creation_history(
            history
        )

        existing = {
            star.id for star in restored.starry_sky
        }

        next_star = restored.create_primordial_star()

        self.assertNotIn(next_star.id, existing)
        self.assertTrue(
            next_star.id.endswith(":primordial_star:4")
        )

        next_epoch = (
            restored.run_primordial_stellar_epoch(
                star_count=1,
            )
        )

        self.assertTrue(
            next_epoch.primordial_nebula.id.endswith(
                ":primordial_nebula:2"
            )
        )

    def test_multiple_nebulae_replay_latest_one(self):
        source = self._layer()

        first = source.run_primordial_stellar_epoch(
            star_count=1,
        )

        second = source.run_primordial_stellar_epoch(
            star_count=2,
        )

        restored = self._layer()

        stars, nebula = (
            restored.replay_primordial_creation_history(
                source.primordial_creation_history
            )
        )

        self.assertEqual(len(stars), 3)
        self.assertNotEqual(
            first.primordial_nebula.id,
            second.primordial_nebula.id,
        )
        self.assertEqual(
            nebula.id,
            second.primordial_nebula.id,
        )
        self.assertEqual(
            restored.primordial_identity_cursor.nebula_serial,
            2,
        )

    def test_remnant_history_is_detached(self):
        source = self._layer()

        result = source.run_primordial_stellar_epoch(
            star_count=1,
        )

        event = (
            source.primordial_creation_history.events[-1]
        )

        saved = event.remnants[0].elemental_potentials

        result.primordial_nebula.source_remnants[
            0
        ].elemental_potentials["carbon"] = 99.0

        self.assertEqual(
            saved,
            (
                ("carbon", 1.0),
                ("hydrogen", 1.0),
            ),
        )

        restored = self._layer()

        _, nebula = (
            restored.replay_primordial_creation_history(
                source.primordial_creation_history
            )
        )

        self.assertEqual(
            nebula.elemental_potentials["carbon"],
            1.0,
        )

    def test_historical_memory_accepts_replayed_objects(self):
        source = self._layer()

        source.run_primordial_stellar_epoch(
            star_count=1,
        )

        restored = self._layer()

        stars, nebula = (
            restored.replay_primordial_creation_history(
                source.primordial_creation_history
            )
        )

        memory = GodSharedMemory()

        memory.record(
            QuantumDirectorStarCreatedEvent(
                subject=stars[0],
            )
        )

        memory.record(
            QuantumDirectorNebulaCreatedEvent(
                subject=nebula,
            )
        )

        self.assertEqual(
            memory.fact_at(0).value_for("subject.id"),
            stars[0].id,
        )

        self.assertEqual(
            memory.fact_at(1).value_for("subject.id"),
            nebula.id,
        )

    def test_rejects_skipped_id_atomically(self):
        target = self._layer()

        original_cursor = target.primordial_identity_cursor
        original_history = target.primordial_creation_history

        malformed = PrimordialCreationHistory(
            scope=original_cursor.scope,
            events=(
                PrimordialStarCreated(
                    object_id=(
                        original_cursor.scope
                        + ":primordial_star:2"
                    )
                ),
            ),
        )

        with self.assertRaises(ValueError):
            target.replay_primordial_creation_history(
                malformed
            )

        self.assertIs(
            target.primordial_identity_cursor,
            original_cursor,
        )
        self.assertIs(
            target.primordial_creation_history,
            original_history,
        )
        self.assertEqual(target.starry_sky, [])
        self.assertIsNone(target.primordial_nebula)

    def test_rejects_invalid_transition_atomically(self):
        target = self._layer()
        cursor = target.primordial_identity_cursor

        malformed = PrimordialCreationHistory(
            scope=cursor.scope,
            events=(
                PrimordialStarCreated(
                    object_id=(
                        cursor.scope
                        + ":primordial_star:1"
                    )
                ),
                PrimordialStarTransition(
                    object_id=(
                        cursor.scope
                        + ":primordial_star:1"
                    ),
                    state=PrimordialIdeaStarState.EXPLODED,
                ),
            ),
        )

        with self.assertRaises(ValueError):
            target.replay_primordial_creation_history(
                malformed
            )

        self.assertEqual(target.starry_sky, [])
        self.assertEqual(
            target.primordial_identity_cursor.star_serial,
            0,
        )

    def test_rejects_foreign_history(self):
        source = self._layer("foreign")
        target = self._layer("target")

        source.create_primordial_star()

        initial = target.primordial_identity_cursor

        with self.assertRaises(ValueError):
            target.replay_primordial_creation_history(
                source.primordial_creation_history
            )

        self.assertIs(
            target.primordial_identity_cursor,
            initial,
        )

    def test_rejects_replay_into_populated_layer(self):
        layer = self._layer()

        layer.create_primordial_star()

        with self.assertRaises(RuntimeError):
            layer.replay_primordial_creation_history(
                layer.primordial_creation_history
            )

    def test_rejects_mapping_history(self):
        layer = self._layer()

        with self.assertRaises(TypeError):
            layer.replay_primordial_creation_history({
                "scope": layer.primordial_identity_cursor.scope,
                "events": [],
            })

    def test_rejects_untyped_history_event(self):
        scope = "creation_replay:idea_universe:1"

        with self.assertRaises(TypeError):
            PrimordialCreationHistory(
                scope=scope,
                events=({"object_id": "legacy"},),
            )

    def test_remnant_fact_rejects_mutable_potentials(self):
        with self.assertRaises(TypeError):
            PrimordialRemnantCreation(
                source_star_id="test:star:1",
                source="star",
                elemental_potentials={
                    "carbon": 1.0,
                },
            )


if __name__ == "__main__":
    unittest.main()
