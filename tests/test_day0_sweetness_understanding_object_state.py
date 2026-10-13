import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_sweetness_understanding_state import (
    GodFinishesSerpentsMeadEvent,
    LilithExplainsSweetnessEvent,
    MeadSweetnessAssessmentState,
    SweetnessUnderstandingState,
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


class Day0SweetnessUnderstandingObjectStateTests(
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

    def test_lilith_explanation_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_balanced_acidity_idea()

        scene.god_tastes_existing_wine_and_rejects_it()

        event = (
            scene.lilith_explains_sweetness_to_god()
        )

        self.assertIsInstance(
            event,
            LilithExplainsSweetnessEvent,
        )

        self.assertEqual(
            event.principle,
            "sweetness",
        )

        self.assertTrue(
            scene.god
            .bar_knowledge
            .sweetness_explained
        )

        self._assert_object_only(
            event,
            "principle",
        )

    def test_mead_understanding_is_fully_object_state(
        self
    ):
        scene = self._scene()

        scene.advance_to_balanced_acidity_idea()

        scene.god_tastes_existing_wine_and_rejects_it()

        scene.lilith_explains_sweetness_to_god()

        event = (
            scene
            .god_finishes_serpents_mead_and_understands_sweetness()
        )

        self.assertIsInstance(
            event,
            GodFinishesSerpentsMeadEvent,
        )

        self.assertIsInstance(
            event.understands,
            SweetnessUnderstandingState,
        )

        self.assertIsInstance(
            event.assessment,
            MeadSweetnessAssessmentState,
        )

        self.assertTrue(
            event.finished
        )

        self.assertTrue(
            event.understands.sweetness
        )

        self.assertTrue(
            event.assessment.sweet
        )

        self.assertFalse(
            event.assessment.good
        )

        self._assert_object_only(
            event,
            "finished",
        )

        self._assert_object_only(
            event.understands,
            "sweetness",
        )

        self._assert_object_only(
            event.assessment,
            "good",
        )

    def test_god_keeps_typed_sweetness_knowledge(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_understands_sweetness()

        knowledge = (
            scene.god
            .bar_knowledge
            .sweetness
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
            "mead",
        )

        self.assertTrue(
            knowledge.example_is_sweet
        )

        self.assertFalse(
            knowledge.example_is_good
        )

        self._assert_object_only(
            knowledge,
            "understood",
        )

    def test_history_remains_serialized_snapshot(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_understands_sweetness()

        event = next(
            event
            for event in reversed(
                scene.history
            )
            if event["name"]
            == (
                "god_finishes_serpents_mead_"
                "and_understands_sweetness"
            )
        )

        self.assertIsInstance(
            event,
            dict,
        )

        self.assertIsInstance(
            event["understands"],
            dict,
        )

        self.assertIsInstance(
            event["assessment"],
            dict,
        )

        self.assertTrue(
            event["understands"]["sweetness"]
        )

        self.assertFalse(
            event["assessment"]["good"]
        )


if __name__ == "__main__":
    unittest.main()
