import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarGuestKnowledge,
    BarTasteKnowledge,
    BarWagerKnowledge,
    BarWineAssessment,
    BarWineDiscussionKnowledge,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarKnowledgeObjectStateTests(
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

    def test_knowledge_objects_have_no_mapping_api(
        self
    ):
        wager = BarWagerKnowledge(
            known=True,
            source="serpent",
        )
        taste = BarTasteKnowledge(
            understood=True,
            example="mead",
        )
        assessment = BarWineAssessment(
            quality="bad",
            body="watery",
            comparison="water_with_grapes",
        )
        knowledge = BarGuestKnowledge(
            existing_wine=assessment,
            sweetness=taste,
            drink_wager=wager,
        )

        for value, key in (
            (knowledge, "drink_wager"),
            (wager, "known"),
            (taste, "understood"),
            (assessment, "quality"),
        ):
            self._assert_object_only(
                value,
                key
            )

    def test_scene_accumulates_one_knowledge_object(
        self
    ):
        scene = self._scene()
        scene.advance_to_bitterness_split_between_wine_and_beer()
        knowledge = scene.god.bar_knowledge

        self.assertIsInstance(
            knowledge,
            BarGuestKnowledge
        )
        self.assertIsInstance(
            knowledge.wine_discussion,
            BarWineDiscussionKnowledge
        )
        self.assertIsInstance(
            knowledge.existing_wine,
            BarWineAssessment
        )
        self.assertIsInstance(
            knowledge.sweetness,
            BarTasteKnowledge
        )
        self.assertIsInstance(
            knowledge.drink_wager,
            BarWagerKnowledge
        )
        self.assertIsInstance(
            knowledge.bitterness,
            BarTasteKnowledge
        )
        self.assertTrue(
            knowledge.sweetness_explained
        )
        self.assertTrue(
            knowledge.drink_wager.known
        )
        self.assertTrue(
            knowledge.bitterness.understood
        )

    def test_discussion_knowledge_is_detached_copy(
        self
    ):
        scene = self._scene()
        scene.advance_to_god_at_table()
        discussion = (
            scene
            .serpent_lilith_good_drink_discussion
        )

        scene.serpent_explains_wine_discussion_to_god()
        remembered = (
            scene.god.bar_knowledge
            .wine_discussion
        )

        self.assertIsNot(
            remembered.ideas[0],
            discussion.ideas[0]
        )
        remembered.ideas[0].lilith[
            "observation"
        ] = "changed"

        self.assertEqual(
            discussion.ideas[0].lilith[
                "observation"
            ],
            "wine_tastes_like_water"
        )

    def test_assessment_event_is_detached_dict(
        self
    ):
        scene = self._scene()
        scene.advance_to_god_receives_wine()

        event = (
            scene
            .god_tastes_existing_wine_and_rejects_it()
        )
        assessment = (
            scene.god.bar_knowledge
            .existing_wine
        )

        self.assertIsInstance(
            event["assessment"],
            dict
        )
        event["assessment"]["quality"] = (
            "changed"
        )

        self.assertEqual(
            assessment.quality,
            "bad"
        )
        self._assert_object_only(
            assessment,
            "quality"
        )

    def test_public_snapshot_is_detached(
        self
    ):
        knowledge = BarGuestKnowledge(
            sweetness_explained=True,
            sweetness=BarTasteKnowledge(
                understood=True,
                example="mead",
                example_is_sweet=True,
                example_is_good=False,
            ),
            drink_wager=BarWagerKnowledge(
                known=True,
                source="serpent",
            ),
        )

        snapshot = knowledge.to_dict()
        snapshot["sweetness"]["example"] = (
            "changed"
        )
        snapshot["drink_wager"]["source"] = (
            "changed"
        )

        self.assertEqual(
            knowledge.sweetness.example,
            "mead"
        )
        self.assertEqual(
            knowledge.drink_wager.source,
            "serpent"
        )

    def test_bouncer_uses_shared_wager_knowledge(
        self
    ):
        scene = self._scene()
        result = scene.advance_to_bouncer_knows_wager()
        knowledge = (
            scene.meeting_place
            .bouncer
            .wager_knowledge
        )

        self.assertIsInstance(
            knowledge,
            BarWagerKnowledge
        )
        self.assertTrue(
            knowledge.known
        )
        self.assertEqual(
            knowledge.source,
            "serpent"
        )
        self.assertIsInstance(
            result["explanation"],
            dict
        )
        self._assert_object_only(
            knowledge,
            "known"
        )


if __name__ == "__main__":
    unittest.main()
