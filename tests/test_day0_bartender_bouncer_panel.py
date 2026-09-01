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


class Day0BartenderBouncerPanelTests(
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

    def test_lilith_explains_wager_to_bartender(
        self
    ):
        result = (
            self.scene
            .advance_to_bartender_bouncer_panel_proposal()
        )

        explanation = result[
            "explanation"
        ]

        self.assertEqual(
            explanation[
                "speaker"
            ],
            "lilith"
        )

        self.assertEqual(
            explanation[
                "listener"
            ],
            "bartender"
        )

        self.assertEqual(
            explanation[
                "proposal"
            ][
                "judge"
            ],
            "bartender"
        )

    def test_serpent_says_one_judge_is_not_enough(
        self
    ):
        result = (
            self.scene
            .advance_to_bartender_bouncer_panel_proposal()
        )

        self.assertEqual(
            result[
                "objection"
            ][
                "objection"
            ],
            "one_judge_is_not_enough"
        )

    def test_bartender_proposes_bouncer_as_second_taster(
        self
    ):
        result = (
            self.scene
            .advance_to_bartender_bouncer_panel_proposal()
        )

        proposal = result[
            "panel"
        ][
            "proposal"
        ]

        self.assertEqual(
            proposal[
                "type"
            ],
            "tasting_panel"
        )

        self.assertEqual(
            proposal[
                "judges"
            ],
            [
                "bartender",
                "bouncer"
            ]
        )

    def test_panel_is_only_proposed(
        self
    ):
        self.scene.advance_to_bartender_bouncer_panel_proposal()

        proposal = (
            self.scene
            .serpent_lilith_drink_wager
            .tasting_panel_proposal
        )

        self.assertFalse(
            proposal.accepted
        )

    def test_wager_still_has_no_winner(
        self
    ):
        self.scene.advance_to_bartender_bouncer_panel_proposal()

        wager = (
            self.scene
            .serpent_lilith_drink_wager
        )

        self.assertFalse(
            wager.resolved
        )

        self.assertIsNone(
            wager.winner
        )


if __name__ == "__main__":
    unittest.main()
