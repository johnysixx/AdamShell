import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_god_drink_wager_state import (
    DrinkWagerExplanationSnapshot,
    GodAcceptsDrinkWagerEvent,
    SerpentOffersGodWagerParticipationEvent,
    SerpentTellsGodAboutDrinkWagerEvent,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarDrinkWager,
    BarWagerKnowledge,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0GodDrinkWagerObjectStateTests(
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

    def test_explanation_has_detached_typed_snapshot(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_understands_sweetness()

        event = (
            scene.serpent_tells_god_about_drink_wager()
        )

        wager = (
            scene.serpent_lilith_drink_wager
        )

        self.assertIsInstance(
            wager,
            BarDrinkWager,
        )

        self.assertIsInstance(
            event,
            SerpentTellsGodAboutDrinkWagerEvent,
        )

        self.assertIsInstance(
            event.wager,
            DrinkWagerExplanationSnapshot,
        )

        self.assertEqual(
            event.wager.participants,
            (
                "serpent",
                "lilith",
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

        wager.participants.append(
            "changed"
        )

        self.assertEqual(
            event.wager.participants,
            (
                "serpent",
                "lilith",
            ),
        )

        self._assert_object_only(
            event,
            "wager",
        )

        self._assert_object_only(
            event.wager,
            "participants",
        )

    def test_offer_is_runtime_object_state(
        self
    ):
        scene = self._scene()

        scene.advance_to_god_understands_sweetness()

        scene.serpent_tells_god_about_drink_wager()

        offer = (
            scene
            .serpent_offers_god_wager_participation()
        )

        self.assertIsInstance(
            offer,
            SerpentOffersGodWagerParticipationEvent,
        )

        self.assertIsNone(
            offer.accepted
        )

        self.assertIs(
            scene.god_wager_participation_offer,
            offer,
        )

        self._assert_object_only(
            offer,
            "accepted",
        )

    def test_acceptance_updates_offer_and_wager(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_three_way_drink_wager()
        )

        offer = result[
            "offered"
        ]
        accepted = result[
            "accepted"
        ]

        self.assertIsInstance(
            offer,
            SerpentOffersGodWagerParticipationEvent,
        )

        self.assertIsInstance(
            accepted,
            GodAcceptsDrinkWagerEvent,
        )

        self.assertTrue(
            offer.accepted
        )

        self.assertEqual(
            accepted.participant,
            "god",
        )

        self.assertEqual(
            accepted.participants,
            (
                "serpent",
                "lilith",
                "god",
            ),
        )

        self.assertEqual(
            scene.serpent_lilith_drink_wager
            .participants,
            [
                "serpent",
                "lilith",
                "god",
            ],
        )

        self.assertTrue(
            scene.god
            .bar_state
            .participates_in_drink_wager
        )

        self._assert_object_only(
            accepted,
            "participants",
        )

    def test_god_keeps_typed_wager_knowledge(
        self
    ):
        scene = self._scene()

        scene.advance_to_three_way_drink_wager()

        knowledge = (
            scene.god
            .bar_knowledge
            .drink_wager
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

    def test_history_keeps_offer_time_snapshot(
        self
    ):
        scene = self._scene()

        scene.advance_to_three_way_drink_wager()

        snapshot = next(
            event
            for event in scene.history
            if event["name"]
            == (
                "serpent_offers_god_"
                "wager_participation"
            )
        )

        self.assertIsInstance(
            snapshot,
            dict,
        )

        self.assertIsNone(
            snapshot["accepted"]
        )

        self.assertTrue(
            scene.god_wager_participation_offer
            .accepted
        )


if __name__ == "__main__":
    unittest.main()
