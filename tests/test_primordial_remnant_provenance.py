import unittest
from dataclasses import replace

from idea_universe import IdeaUniverse
from idea_universe.primordial_creation_history import (
    PrimordialCreationHistory,
    PrimordialNebulaCreated,
    PrimordialRemnantCreation,
    PrimordialStarCreated,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class PrimordialRemnantProvenanceTests(unittest.TestCase):

    def _layer(self):
        universe = Universe(
            universe_id="provenance_replay"
        )
        universe.universe_registry = UniverseRegistry()

        layer = IdeaUniverse(universe)
        layer.stellar_epoch_started = True
        return layer

    def _history_with_replaced_event(
        self, history, index, replacement
    ):
        events = list(history.events)
        events[index] = replacement

        return PrimordialCreationHistory(
            scope=history.scope,
            events=tuple(events),
        )

    def _assert_rejected_atomically(
        self, malformed, message
    ):
        target = self._layer()

        initial_cursor = target.primordial_identity_cursor
        initial_history = target.primordial_creation_history
        initial_world = target.universe.world[
            "idea_universe"
        ]

        with self.assertRaisesRegex(
            ValueError, message
        ):
            target.replay_primordial_creation_history(
                malformed
            )

        self.assertIs(
            target.primordial_identity_cursor,
            initial_cursor,
        )
        self.assertIs(
            target.primordial_creation_history,
            initial_history,
        )
        self.assertIs(
            target.universe.world["idea_universe"],
            initial_world,
        )
        self.assertEqual(target.starry_sky, [])
        self.assertIsNone(target.primordial_nebula)

    def test_real_explosions_record_distinct_source_ids(self):
        layer = self._layer()

        result = layer.run_primordial_stellar_epoch(
            star_count=2
        )

        event = layer.primordial_creation_history.events[-1]

        self.assertIsInstance(
            event, PrimordialNebulaCreated
        )

        self.assertEqual(
            tuple(r.source_star_id for r in event.remnants),
            tuple(star.id for star in result.stars),
        )

        self.assertNotEqual(
            event.remnants[0].source_star_id,
            event.remnants[1].source_star_id,
        )

        target = self._layer()
        stars, nebula = (
            target.replay_primordial_creation_history(
                layer.primordial_creation_history
            )
        )

        self.assertEqual(
            tuple(star.id for star in stars),
            tuple(star.id for star in result.stars),
        )

        self.assertEqual(
            nebula.elemental_potentials,
            result.primordial_nebula.elemental_potentials,
        )

    def test_rejects_phantom_star_remnant(self):
        target = self._layer()
        scope = target.primordial_identity_cursor.scope

        malformed = PrimordialCreationHistory(
            scope=scope,
            events=(
                PrimordialNebulaCreated(
                    object_id=(
                        f"{scope}:primordial_nebula:1"
                    ),
                    remnants=(
                        PrimordialRemnantCreation(
                            source_star_id=(
                                f"{scope}:primordial_star:99"
                            ),
                            source="phantom_star",
                            elemental_potentials=(
                                ("carbon", 1.0),
                                ("hydrogen", 1.0),
                            ),
                        ),
                    ),
                ),
            ),
        )

        self._assert_rejected_atomically(
            malformed,
            "unknown or already consumed explosion",
        )

    def test_rejects_duplicate_remnant(self):
        source = self._layer()
        source.run_primordial_stellar_epoch(
            star_count=1
        )

        history = source.primordial_creation_history
        original = history.events[-1]
        remnant = original.remnants[0]

        forged = replace(
            original,
            remnants=(remnant, remnant),
        )

        malformed = self._history_with_replaced_event(
            history, -1, forged
        )

        self._assert_rejected_atomically(
            malformed,
            "Duplicate primordial star remnant",
        )

    def test_rejects_altered_elemental_content(self):
        source = self._layer()
        source.run_primordial_stellar_epoch(
            star_count=1
        )

        history = source.primordial_creation_history
        original = history.events[-1]

        forged_remnant = replace(
            original.remnants[0],
            elemental_potentials=(
                ("carbon", 99.0),
                ("hydrogen", 1.0),
            ),
        )

        malformed = self._history_with_replaced_event(
            history,
            -1,
            replace(
                original,
                remnants=(forged_remnant,),
            ),
        )

        self._assert_rejected_atomically(
            malformed,
            "contents do not match explosion",
        )

    def test_rejects_wrong_source_name(self):
        source = self._layer()
        source.run_primordial_stellar_epoch(
            star_count=1
        )

        history = source.primordial_creation_history
        original = history.events[-1]

        forged_remnant = replace(
            original.remnants[0],
            source="different_star",
        )

        malformed = self._history_with_replaced_event(
            history,
            -1,
            replace(
                original,
                remnants=(forged_remnant,),
            ),
        )

        self._assert_rejected_atomically(
            malformed,
            "provenance or elemental",
        )

    def test_rejects_unexploded_star_remnant(self):
        source = self._layer()
        star = source.create_primordial_star()
        history = source.primordial_creation_history

        forged_event = PrimordialNebulaCreated(
            object_id=(
                f"{history.scope}:primordial_nebula:1"
            ),
            remnants=(
                PrimordialRemnantCreation(
                    source_star_id=star.id,
                    source=star.name,
                    elemental_potentials=(
                        ("carbon", 1.0),
                        ("hydrogen", 1.0),
                    ),
                ),
            ),
        )

        malformed = history.with_event(forged_event)

        self._assert_rejected_atomically(
            malformed,
            "unknown or already consumed explosion",
        )

    def test_rejects_missing_explosion_remnant(self):
        source = self._layer()
        source.run_primordial_stellar_epoch(
            star_count=2
        )

        history = source.primordial_creation_history
        original = history.events[-1]

        malformed = self._history_with_replaced_event(
            history,
            -1,
            replace(
                original,
                remnants=original.remnants[:1],
            ),
        )

        self._assert_rejected_atomically(
            malformed,
            "consume all pending explosion remnants",
        )

    def test_rejects_reusing_consumed_remnant(self):
        source = self._layer()

        source.run_primordial_stellar_epoch(
            star_count=1
        )
        first_nebula_event = (
            source.primordial_creation_history.events[-1]
        )

        source.run_primordial_stellar_epoch(
            star_count=1
        )
        history = source.primordial_creation_history
        second_nebula_event = history.events[-1]

        malformed = self._history_with_replaced_event(
            history,
            -1,
            replace(
                second_nebula_event,
                remnants=first_nebula_event.remnants,
            ),
        )

        self._assert_rejected_atomically(
            malformed,
            "unknown or already consumed explosion",
        )

    def test_two_valid_epochs_remain_replayable(self):
        source = self._layer()

        source.run_primordial_stellar_epoch(
            star_count=1
        )
        source.run_primordial_stellar_epoch(
            star_count=2
        )

        target = self._layer()
        stars, nebula = (
            target.replay_primordial_creation_history(
                source.primordial_creation_history
            )
        )

        self.assertEqual(len(stars), 3)
        self.assertEqual(
            nebula.id,
            source.primordial_nebula.id,
        )
        self.assertEqual(
            target.primordial_identity_cursor,
            source.primordial_identity_cursor,
        )

    def test_empty_stellar_epoch_remains_supported(self):
        source = self._layer()

        result = source.run_primordial_stellar_epoch(
            star_count=0
        )

        self.assertEqual(result.stars, ())
        self.assertEqual(result.remnants, ())

        target = self._layer()
        stars, nebula = (
            target.replay_primordial_creation_history(
                source.primordial_creation_history
            )
        )

        self.assertEqual(stars, ())
        self.assertEqual(
            nebula.id,
            result.primordial_nebula.id,
        )
        self.assertEqual(
            nebula.source_remnant_count,
            0,
        )

    def test_remnant_requires_canonical_source_id(self):
        for bad_id in ("", "   ", None, 123):
            with self.subTest(bad_id=repr(bad_id)):
                with self.assertRaises(ValueError):
                    PrimordialRemnantCreation(
                        source_star_id=bad_id,
                        source="star",
                        elemental_potentials=(),
                    )


if __name__ == "__main__":
    unittest.main()
