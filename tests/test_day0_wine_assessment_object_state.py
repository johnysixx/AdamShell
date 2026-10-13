import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_wine_assessment_state import (
    GodTastesExistingWineEvent,
    SerpentModerateAcidityEvent,
    SerpentModerateAcidityResult,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarDrinkIdea,
    BarWineAssessment,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0WineAssessmentObjectStateTests(
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

    def test_balanced_acidity_result_is_object_only(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_balanced_acidity_idea()
            .balance
        )

        self.assertIsInstance(
            result,
            SerpentModerateAcidityResult,
        )

        self.assertIsInstance(
            result.idea,
            BarDrinkIdea,
        )

        self.assertIsInstance(
            result.event,
            SerpentModerateAcidityEvent,
        )

        self.assertEqual(
            result.idea.qualification.acidity,
            "moderate",
        )

        self.assertEqual(
            result.event.desired_acidity,
            "moderate",
        )

        self._assert_object_only(
            result,
            "idea",
        )

        self._assert_object_only(
            result.event,
            "desired_acidity",
        )

    def test_existing_wine_assessment_event_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_balanced_acidity_idea()

        event = (
            scene
            .god_tastes_existing_wine_and_rejects_it()
        )

        knowledge_assessment = (
            scene.god
            .bar_knowledge
            .existing_wine
        )

        self.assertIsInstance(
            event,
            GodTastesExistingWineEvent,
        )

        self.assertIsInstance(
            event.assessment,
            BarWineAssessment,
        )

        self.assertIsInstance(
            knowledge_assessment,
            BarWineAssessment,
        )

        self.assertIsNot(
            event.assessment,
            knowledge_assessment,
        )

        self.assertEqual(
            event.assessment.quality,
            "bad",
        )

        self.assertEqual(
            event.assessment.body,
            "watery",
        )

        self.assertEqual(
            event.assessment.comparison,
            (
                "water_in_which_someone_"
                "soaked_grapes"
            ),
        )

        self._assert_object_only(
            event,
            "assessment",
        )

        self._assert_object_only(
            event.assessment,
            "quality",
        )


if __name__ == "__main__":
    unittest.main()
