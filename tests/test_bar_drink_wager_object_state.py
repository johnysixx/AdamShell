import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarDrinkWager,
    BarDrinkWagerChallenge,
    BarDrinkWagerStakes,
    BarWagerDecisionMethod,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarDrinkWagerObjectStateTests(
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

    def test_wager_graph_is_object_only(
        self
    ):
        wager = BarDrinkWager()

        self.assertIsInstance(
            wager.challenge,
            BarDrinkWagerChallenge
        )
        self.assertIsInstance(
            wager.stakes,
            BarDrinkWagerStakes
        )
        self.assertEqual(
            wager.challenge.eligible_drinks,
            [
                "wine",
                "beer",
                "mead",
            ]
        )
        self._assert_object_only(
            wager,
            "accepted"
        )
        self._assert_object_only(
            wager.challenge,
            "eligible_drinks"
        )
        self._assert_object_only(
            wager.stakes,
            "loser"
        )

    def test_wager_mutations_preserve_identity(
        self
    ):
        wager = BarDrinkWager()

        accepted = wager.accept(
            participant="lilith"
        )
        extended = wager.add_participant(
            participant="god",
            wager_type=
                "three_way_drink_wager"
        )

        self.assertIs(
            accepted,
            wager
        )
        self.assertIs(
            extended,
            wager
        )
        self.assertTrue(
            wager.accepted
        )
        self.assertEqual(
            wager.accepted_by,
            "lilith"
        )
        self.assertEqual(
            wager.participants,
            [
                "serpent",
                "lilith",
                "god",
            ]
        )

    def test_snapshot_is_detached_boundary_dict(
        self
    ):
        wager = BarDrinkWager()
        proposal = BarWagerDecisionMethod(
            type="participant_vote",
            voters=[
                "serpent",
                "lilith",
            ],
            proposed=True,
            accepted=False,
        )
        wager.decision_method_proposal = (
            proposal
        )

        snapshot = wager.to_dict()

        snapshot["participants"].append(
            "bartender"
        )
        snapshot["challenge"][
            "eligible_drinks"
        ].append(
            "water"
        )
        snapshot[
            "decision_method_proposal"
        ]["voters"].append(
            "god"
        )

        self.assertEqual(
            wager.participants,
            [
                "serpent",
                "lilith",
            ]
        )
        self.assertNotIn(
            "water",
            wager.challenge.eligible_drinks
        )
        self.assertEqual(
            proposal.voters,
            [
                "serpent",
                "lilith",
            ]
        )
        self._assert_object_only(
            proposal,
            "type"
        )

    def test_scene_emits_detached_wager_snapshot(
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
        scene.advance_to_lilith_entry()
        scene.lilith_orders_vodka_with_lemon()
        scene.serpent_and_lilith_begin_conversation()
        scene.serpent_and_lilith_taste_first_drinks()

        wager = (
            scene
            .serpent_proposes_drink_wager_to_lilith()
        )
        proposal_event = scene.history[-1]
        scene.lilith_accepts_drink_wager()

        self.assertIsInstance(
            proposal_event["wager"],
            dict
        )
        self.assertFalse(
            proposal_event["wager"][
                "accepted"
            ]
        )
        self.assertTrue(
            wager.accepted
        )
        self._assert_object_only(
            wager,
            "accepted"
        )


if __name__ == "__main__":
    unittest.main()
