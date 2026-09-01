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
    BarDrinkIdea,
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
        idea = BarDrinkIdea(
            subject="wine",
            source="lilith",
            desired_property={
                "sweetness": True,
            },
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

    def test_snapshot_is_detached_boundary_dict(
        self
    ):
        discussion = BarDrinkDiscussion()
        idea = discussion.add_idea(
            BarDrinkIdea(
                subject="wine",
                serpent={
                    "proposal":
                        "flavor_should_be_fuller",
                },
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
            idea.serpent["proposal"],
            "flavor_should_be_fuller"
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
