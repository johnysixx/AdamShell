import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarBeerHypothesis,
    BarDrinkDiscussion,
    BarDrinkDesiredProperty,
    BarDrinkAssessment,
    BarDrinkIdea,
    BarDrinkSpeakerContribution,
    BarWineHypothesis,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarDrinkDiscussionObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[key]

    def test_discussion_stores_idea_object(
        self
    ):
        discussion = BarDrinkDiscussion()
        desired_property = BarDrinkDesiredProperty(
            sweetness=True,
        )
        idea = BarDrinkIdea(
            subject="wine",
            source="lilith",
            desired_property=desired_property,
        )

        result = discussion.add_idea(
            idea
        )

        self.assertIs(
            result,
            idea
        )
        self.assertIs(
            discussion.ideas[0],
            idea
        )
        self.assertFalse(
            discussion.resolved
        )
        self._assert_object_only(
            discussion,
            "ideas"
        )
        self._assert_object_only(
            idea,
            "subject"
        )

    def test_hypotheses_are_object_only(
        self
    ):
        wine = BarWineHypothesis(
            sweetness=True,
            acidity="moderate",
        )
        beer = BarBeerHypothesis(
            bitterness="allowed",
        )

        self.assertTrue(
            wine.sweetness
        )
        self.assertEqual(
            wine.acidity,
            "moderate"
        )
        self.assertEqual(
            beer.bitterness,
            "allowed"
        )
        self._assert_object_only(
            wine,
            "sweetness"
        )
        self._assert_object_only(
            beer,
            "bitterness"
        )



    def test_desired_property_is_object_only(
        self
    ):
        desired_property = BarDrinkDesiredProperty(
            sweetness=True,
            acidity=False,
        )
        idea = BarDrinkIdea(
            subject="wine",
            desired_property=desired_property,
        )

        self.assertIs(
            idea.desired_property,
            desired_property,
        )
        self.assertTrue(
            idea.desired_property.sweetness
        )
        self.assertFalse(
            idea.desired_property.acidity
        )
        self._assert_object_only(
            idea.desired_property,
            "sweetness",
        )

    def test_desired_property_mapping_is_rejected(
        self
    ):
        with self.assertRaisesRegex(
            TypeError,
            "BarDrinkDesiredProperty",
        ):
            BarDrinkIdea(
                subject="wine",
                desired_property={
                    "sweetness": True,
                },
            )

    def test_assessment_is_object_only(
        self
    ):
        assessment = BarDrinkAssessment(
            sweetness="good",
            full_body="still_missing",
        )
        idea = BarDrinkIdea(
            subject="wine",
            assessment=assessment,
        )

        self.assertIs(
            idea.assessment,
            assessment,
        )
        self.assertEqual(
            idea.assessment.sweetness,
            "good",
        )
        self.assertEqual(
            idea.assessment.full_body,
            "still_missing",
        )
        self._assert_object_only(
            idea.assessment,
            "sweetness",
        )

    def test_assessment_mapping_is_rejected(
        self
    ):
        with self.assertRaisesRegex(
            TypeError,
            "BarDrinkAssessment",
        ):
            BarDrinkIdea(
                subject="wine",
                assessment={
                    "sweetness": "good",
                },
            )

    def test_speaker_contributions_are_object_only(
        self
    ):
        lilith = BarDrinkSpeakerContribution(
            observation="wine_tastes_like_water",
        )
        serpent = BarDrinkSpeakerContribution(
            agrees=True,
            proposal="flavor_should_be_fuller",
        )
        idea = BarDrinkIdea(
            subject="wine",
            lilith=lilith,
            serpent=serpent,
        )

        self.assertIs(idea.lilith, lilith)
        self.assertIs(idea.serpent, serpent)
        self.assertEqual(
            idea.lilith.observation,
            "wine_tastes_like_water",
        )
        self.assertTrue(idea.serpent.agrees)
        self.assertEqual(
            idea.serpent.proposal,
            "flavor_should_be_fuller",
        )
        self._assert_object_only(
            idea.lilith,
            "observation",
        )
        self._assert_object_only(
            idea.serpent,
            "proposal",
        )

    def test_speaker_mapping_is_rejected(
        self
    ):
        with self.assertRaisesRegex(
            TypeError,
            "BarDrinkSpeakerContribution",
        ):
            BarDrinkIdea(
                subject="wine",
                serpent={
                    "proposal":
                        "flavor_should_be_fuller",
                },
            )

    def test_snapshot_is_detached_boundary_dict(
        self
    ):
        discussion = BarDrinkDiscussion()
        idea = discussion.add_idea(
            BarDrinkIdea(
                subject="wine",
                serpent=BarDrinkSpeakerContribution(
                    proposal="flavor_should_be_fuller",
                ),
                desired_property=BarDrinkDesiredProperty(
                    sweetness=True,
                ),
                assessment=BarDrinkAssessment(
                    sweetness="good",
                    full_body="still_missing",
                ),
            )
        )
        discussion.current_hypothesis = (
            BarWineHypothesis(
                sweetness=True,
                acidity=True,
            )
        )

        snapshot = discussion.to_dict()

        snapshot["participants"].append(
            "god"
        )
        snapshot["ideas"][0][
            "serpent"
        ]["proposal"] = "changed"
        snapshot["ideas"][0][
            "desired_property"
        ]["sweetness"] = False
        snapshot["ideas"][0][
            "assessment"
        ]["sweetness"] = "changed"
        snapshot["current_hypothesis"][
            "acidity"
        ] = False

        self.assertEqual(
            discussion.participants,
            [
                "serpent",
                "lilith",
            ]
        )
        self.assertEqual(
            idea.serpent.proposal,
            "flavor_should_be_fuller"
        )
        self.assertTrue(
            idea.desired_property.sweetness
        )
        self.assertEqual(
            idea.assessment.sweetness,
            "good",
        )
        self.assertTrue(
            discussion
            .current_hypothesis
            .acidity
        )

    def test_scene_keeps_object_and_emits_snapshot(
        self
    ):
        universe = Universe()
        universe.universe_registry = (
            UniverseRegistry()
        )
        scene = Day0FirstBarShift(
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

        result = (
            scene
            .advance_to_good_drink_discussion()
        )
        discussion = result["discussion"]
        event = next(
            item
            for item in scene.history
            if item.get("name")
            == (
                "serpent_lilith_good_"
                "drink_discussion"
            )
        )

        self.assertIsInstance(
            discussion,
            BarDrinkDiscussion
        )
        self.assertIs(
            discussion,
            scene
            .serpent_lilith_good_drink_discussion
        )
        self.assertIsInstance(
            event,
            dict
        )

        event["subjects"].append(
            "water"
        )

        self.assertNotIn(
            "water",
            discussion.subjects
        )
        self._assert_object_only(
            discussion,
            "subjects"
        )


if __name__ == "__main__":
    unittest.main()
