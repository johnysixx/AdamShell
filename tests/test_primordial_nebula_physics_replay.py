import unittest
from dataclasses import replace

from idea_universe import IdeaUniverse
from idea_universe.primordial_creation_history import (
    PrimordialCreationHistory,
    PrimordialNebulaPhysicsEvent,
)
from idea_universe.primordial_nebula import (
    PrimordialNebula,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class PrimordialNebulaPhysicsReplayTests(unittest.TestCase):

    def _layer(self):
        universe = Universe(
            universe_id="nebula_physics_replay"
        )
        universe.universe_registry = UniverseRegistry()

        layer = IdeaUniverse(universe)
        layer.stellar_epoch_started = True

        return layer

    def _evolve(self, layer):
        epoch = layer.run_primordial_stellar_epoch(
            star_count=1
        )

        nebula = epoch.primordial_nebula

        nebula.size = 100.0

        self.assertEqual(
            nebula.form_hydrocarbons(),
            1.0,
        )

        self.assertEqual(
            nebula.form_liquid_hydrocarbons(),
            1.0,
        )

        nebula.record_liquid_hydrocarbon_level(
            100.0
        )

        nebula.record_liquid_hydrocarbon_level(
            130.0
        )

        self.assertEqual(
            nebula.mine_liquid_hydrocarbons(3.0),
            3.0,
        )

        layer.tick()

        return nebula

    def test_replay_restores_all_six_physical_fields(self):
        source = self._layer()
        original = self._evolve(source)

        history = source.primordial_creation_history

        restored = self._layer()

        _, replayed = (
            restored.replay_primordial_creation_history(
                history
            )
        )

        fields = (
            "tick_count",
            "size",
            "elemental_potentials",
            "previous_liquid_hydrocarbon_level",
            "current_liquid_hydrocarbon_level",
            "mined_from_current_growth",
        )

        original_state = original.public_state
        restored_state = replayed.public_state

        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(
                    original_state[field],
                    restored_state[field],
                )

        self.assertEqual(original.id, replayed.id)
        self.assertIs(
            restored.primordial_creation_history,
            history,
        )

    def test_physics_events_are_typed_and_frozen(self):
        source = self._layer()
        self._evolve(source)

        events = [
            event
            for event
            in source.primordial_creation_history.events
            if isinstance(
                event,
                PrimordialNebulaPhysicsEvent,
            )
        ]

        self.assertEqual(len(events), 7)

        self.assertEqual(
            [event.operation for event in events],
            [
                "set_size",
                "form_hydrocarbons",
                "form_liquid_hydrocarbons",
                "record_liquid_hydrocarbon_level",
                "record_liquid_hydrocarbon_level",
                "mine_liquid_hydrocarbons",
                "tick",
            ],
        )

        for event in events:
            with self.assertRaises(
                Exception
            ):
                event.operation = "changed"

            self.assertFalse(
                hasattr(event, "get")
            )

    def test_replay_continuation_records_new_operations(self):
        source = self._layer()
        self._evolve(source)

        restored = self._layer()

        _, nebula = (
            restored.replay_primordial_creation_history(
                source.primordial_creation_history
            )
        )

        count_before = len(
            restored.primordial_creation_history.events
        )

        nebula.tick()
        nebula.size = 150.0

        self.assertEqual(
            len(restored.primordial_creation_history.events),
            count_before + 2,
        )

        another = self._layer()

        _, replayed = (
            another.replay_primordial_creation_history(
                restored.primordial_creation_history
            )
        )

        self.assertEqual(replayed.tick_count, 2)
        self.assertEqual(replayed.size, 150.0)

    def test_rejects_forged_mining_above_limit(self):
        source = self._layer()
        self._evolve(source)

        history = source.primordial_creation_history

        events = list(history.events)

        index = next(
            i for i, event in enumerate(events)
            if (
                isinstance(
                    event,
                    PrimordialNebulaPhysicsEvent,
                )
                and event.operation
                == "mine_liquid_hydrocarbons"
            )
        )

        events[index] = replace(
            events[index],
            value=4.0,
            result=4.0,
        )

        malformed = PrimordialCreationHistory(
            scope=history.scope,
            events=tuple(events),
        )

        target = self._layer()

        original_cursor = target.primordial_identity_cursor
        original_history = target.primordial_creation_history

        with self.assertRaises(RuntimeError):
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

    def test_rejects_forged_result_atomically(self):
        source = self._layer()
        self._evolve(source)

        history = source.primordial_creation_history

        events = list(history.events)

        index = next(
            i for i, event in enumerate(events)
            if (
                isinstance(
                    event,
                    PrimordialNebulaPhysicsEvent,
                )
                and event.operation
                == "mine_liquid_hydrocarbons"
            )
        )

        events[index] = replace(
            events[index],
            result=999.0,
        )

        malformed = PrimordialCreationHistory(
            scope=history.scope,
            events=tuple(events),
        )

        target = self._layer()

        with self.assertRaisesRegex(
            ValueError,
            "result mismatch",
        ):
            target.replay_primordial_creation_history(
                malformed
            )

        self.assertEqual(target.starry_sky, [])
        self.assertIsNone(target.primordial_nebula)

    def test_rejects_unknown_nebula(self):
        target = self._layer()

        scope = target.primordial_identity_cursor.scope

        malformed = PrimordialCreationHistory(
            scope=scope,
            events=(
                PrimordialNebulaPhysicsEvent(
                    object_id=(
                        f"{scope}:primordial_nebula:999"
                    ),
                    operation="tick",
                    result=1,
                ),
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "unknown nebula",
        ):
            target.replay_primordial_creation_history(
                malformed
            )

        self.assertEqual(target.starry_sky, [])

    def test_multiple_nebulae_keep_independent_history(self):
        source = self._layer()

        first = source.run_primordial_stellar_epoch(
            star_count=1
        ).primordial_nebula

        second = source.run_primordial_stellar_epoch(
            star_count=1
        ).primordial_nebula

        first.size = 100.0
        second.size = 200.0

        first.tick()
        second.tick()

        target = self._layer()

        _, latest = (
            target.replay_primordial_creation_history(
                source.primordial_creation_history
            )
        )

        self.assertEqual(latest.id, second.id)
        self.assertEqual(latest.size, 200.0)
        self.assertEqual(latest.tick_count, 1)

    def test_direct_unowned_nebula_still_works(self):
        nebula = PrimordialNebula()

        nebula.size = 100.0
        nebula.record_liquid_hydrocarbon_level(
            100.0
        )
        nebula.record_liquid_hydrocarbon_level(
            130.0
        )

        self.assertEqual(
            nebula.mine_liquid_hydrocarbons(3.0),
            3.0,
        )

        self.assertEqual(
            nebula.current_liquid_hydrocarbon_level,
            127.0,
        )

    def test_invalid_event_operation_rejected(self):
        with self.assertRaises(ValueError):
            PrimordialNebulaPhysicsEvent(
                object_id="nebula:1",
                operation="overwrite_state",
                result=1.0,
            )


if __name__ == "__main__":
    unittest.main()
