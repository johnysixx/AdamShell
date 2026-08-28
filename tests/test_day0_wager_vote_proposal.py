import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift
)


class Day0WagerVoteProposalTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.bar = MeetingPlace(
            self.universe
        )

        self.scene = Day0FirstBarShift(
            universe=self.universe,
            meeting_place=self.bar,
            library=Library(
                self.universe
            ),
            gods=Gods(
                self.universe
            ),
            idea_entities=IdeaEntities(
                self.universe
            )
        )

    def test_god_asks_who_decides_winner(
        self
    ):
        result = (
            self.scene
            .advance_to_wager_vote_proposal()
        )

        self.assertEqual(
            result[
                "question"
            ][
                "question"
            ],
            "who_decides_winner"
        )

    def test_lilith_proposes_vote_between_participants(
        self
    ):
        result = (
            self.scene
            .advance_to_wager_vote_proposal()
        )

        method = (
            result[
                "proposal"
            ][
                "decision_method"
            ]
        )

        self.assertEqual(
            method[
                "type"
            ],
            "participant_vote"
        )

        self.assertEqual(
            method[
                "voters"
            ],
            [
                "serpent",
                "lilith",
                "god"
            ]
        )

    def test_vote_is_only_proposed_not_yet_accepted(
        self
    ):
        self.scene.advance_to_wager_vote_proposal()

        method = (
            self.scene
            .serpent_lilith_drink_wager[
                "decision_method_proposal"
            ]
        )

        self.assertTrue(
            method[
                "proposed"
            ]
        )

        self.assertFalse(
            method[
                "accepted"
            ]
        )

    def test_wager_remains_unresolved(
        self
    ):
        self.scene.advance_to_wager_vote_proposal()

        wager = (
            self.scene
            .serpent_lilith_drink_wager
        )

        self.assertFalse(
            wager[
                "resolved"
            ]
        )

        self.assertIsNone(
            wager[
                "winner"
            ]
        )


if __name__ == "__main__":
    unittest.main()
