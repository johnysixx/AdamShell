import unittest

from genesis.day0_beer_bitterness_state import (
    BeerBitternessConclusionState,
    BeerTasteAssessmentState,
    BitternessUnderstandingState,
    GodTastesBeerAndUnderstandsBitternessEvent,
    LilithSipsLilithAndReactsToBeerEvent,
    WineBitternessConclusionState,
)
from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarTasteKnowledge,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0BeerBitternessObjectStateTests(
    unittest.TestCase
):

    def _scene(self):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        return Day0FirstBarShift(
            universe=universe,
            meeting_place=MeetingPlace(
                universe
            ),
            library=Library(
                universe
            ),
            gods=Gods(
                universe
            ),
            idea_entities=IdeaEntities(
                universe
            ),
        )

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

    def test_god_beer_tasting_is_fully_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bitterness_split_between_wine_and_beer()
        )

        event = result.god_beer

        self.assertIsInstance(
            event,
            GodTastesBeerAndUnderstandsBitternessEvent,
        )

        self.assertIsInstance(
            event.assessment,
            BeerTasteAssessmentState,
        )

        self.assertIsInstance(
            event.understands,
            BitternessUnderstandingState,
        )

        self.assertIsInstance(
            event.wine_conclusion,
            WineBitternessConclusionState,
        )

        self.assertTrue(
            event.assessment.not_so_bad
        )

        self.assertTrue(
            event.understands.bitterness
        )

        self.assertFalse(
            event.wine_conclusion
            .bitterness_belongs_in_wine
        )

        self._assert_object_only(
            event,
            "assessment",
        )

        self._assert_object_only(
            event.assessment,
            "not_so_bad",
        )

        self._assert_object_only(
            event.understands,
            "bitterness",
        )

        self._assert_object_only(
            event.wine_conclusion,
            "bitterness_belongs_in_wine",
        )

    def test_god_keeps_typed_bitterness_knowledge(
        self
    ):
        scene = self._scene()

        scene.advance_to_bitterness_split_between_wine_and_beer()

        knowledge = (
            scene.god
            .bar_knowledge
            .bitterness
        )

        self.assertIsInstance(
            knowledge,
            BarTasteKnowledge,
        )

        self.assertTrue(
            knowledge.understood
        )

        self.assertEqual(
            knowledge.example,
            "beer",
        )

        self._assert_object_only(
            knowledge,
            "understood",
        )

    def test_lilith_beer_reaction_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bitterness_split_between_wine_and_beer()
        )

        event = result.lilith

        self.assertIsInstance(
            event,
            LilithSipsLilithAndReactsToBeerEvent,
        )

        self.assertIsInstance(
            event.beer_conclusion,
            BeerBitternessConclusionState,
        )

        self.assertTrue(
            event.disagrees_beer_is_good
        )

        self.assertTrue(
            event.beer_conclusion
            .bitterness_allowed
        )

        self.assertTrue(
            event.effects_applied
        )

        self._assert_object_only(
            event,
            "beer_conclusion",
        )

        self._assert_object_only(
            event.beer_conclusion,
            "bitterness_allowed",
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        scene.advance_to_bitterness_split_between_wine_and_beer()

        god_event = next(
            event
            for event in scene.checkpoint()["history"]
            if event["name"]
            == (
                "god_tastes_beer_and_"
                "understands_bitterness"
            )
        )

        lilith_event = next(
            event
            for event in scene.checkpoint()["history"]
            if event["name"]
            == (
                "lilith_sips_lilith_"
                "and_reacts_to_beer"
            )
        )

        self.assertIsInstance(
            god_event,
            dict,
        )

        self.assertIsInstance(
            god_event["assessment"],
            dict,
        )

        self.assertIsInstance(
            god_event["understands"],
            dict,
        )

        self.assertIsInstance(
            god_event["wine_conclusion"],
            dict,
        )

        self.assertIsInstance(
            lilith_event,
            dict,
        )

        self.assertIsInstance(
            lilith_event["beer_conclusion"],
            dict,
        )


if __name__ == "__main__":
    unittest.main()
