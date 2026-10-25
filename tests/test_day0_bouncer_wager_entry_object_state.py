import unittest

from genesis.day0_bouncer_wager_entry_state import (
    BouncerEntersBarWithGarfieldEvent,
    SerpentExplainsWagerToBouncerEvent,
)
from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarWagerKnowledge,
)
from meeting_place.bouncer_state import (
    BouncerState,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0BouncerWagerEntryObjectStateTests(
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

    def test_bouncer_entry_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bouncer_inside_after_garfield()
        )

        event = result.bouncer

        bouncer = (
            scene.meeting_place.bouncer
        )

        self.assertIsInstance(
            event,
            BouncerEntersBarWithGarfieldEvent,
        )

        self.assertEqual(
            event.locations,
            (
                "outside_bar",
                "inside_bar",
            ),
        )

        self.assertEqual(
            event.with_cat,
            "garfield",
        )

        self.assertIs(
            bouncer.state,
            BouncerState.INSIDE_AND_OUTSIDE_BAR,
        )

        self.assertEqual(
            bouncer.locations,
            [
                "outside_bar",
                "inside_bar",
            ],
        )

        self.assertTrue(
            bouncer.guards_entrance
        )

        self.assertTrue(
            bouncer.present_in_bar
        )

        proposal = (
            scene.serpent_lilith_drink_wager
            .tasting_panel_proposal
        )

        self.assertTrue(
            proposal.bouncer_present
        )

        self._assert_object_only(
            event,
            "locations",
        )

    def test_wager_explanation_is_object_state(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .advance_to_bouncer_knows_wager()
        )

        event = result.explanation

        self.assertIsInstance(
            event,
            SerpentExplainsWagerToBouncerEvent,
        )

        self.assertEqual(
            event.participants,
            (
                "serpent",
                "lilith",
                "god",
            ),
        )

        self.assertEqual(
            event.contest,
            (
                "wine",
                "mead",
                "beer",
            ),
        )

        self.assertEqual(
            event.proposed_judges,
            (
                "bartender",
                "bouncer",
            ),
        )

        self._assert_object_only(
            event,
            "participants",
        )

    def test_bouncer_keeps_typed_wager_knowledge(
        self
    ):
        scene = self._scene()

        scene.advance_to_bouncer_knows_wager()

        knowledge = (
            scene.meeting_place
            .bouncer
            .wager_knowledge
        )

        self.assertIsInstance(
            knowledge,
            BarWagerKnowledge,
        )

        self.assertTrue(
            knowledge.known
        )

        self.assertEqual(
            knowledge.source,
            "serpent",
        )

        self._assert_object_only(
            knowledge,
            "known",
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        scene.advance_to_bouncer_knows_wager()

        entry = next(
            event
            for event in scene.checkpoint()["history"]
            if (
                isinstance(
                    event,
                    dict,
                )
                and event["name"]
                == "bouncer_enters_bar_with_garfield"
            )
        )

        explanation = next(
            event
            for event in scene.checkpoint()["history"]
            if (
                isinstance(
                    event,
                    dict,
                )
                and event["name"]
                == "serpent_explains_wager_to_bouncer"
            )
        )

        self.assertEqual(
            entry["with"],
            "garfield",
        )

        self.assertEqual(
            entry["locations"],
            [
                "outside_bar",
                "inside_bar",
            ],
        )

        self.assertEqual(
            explanation["participants"],
            [
                "serpent",
                "lilith",
                "god",
            ],
        )

        self.assertEqual(
            explanation["proposed_judges"],
            [
                "bartender",
                "bouncer",
            ],
        )


if __name__ == "__main__":
    unittest.main()
