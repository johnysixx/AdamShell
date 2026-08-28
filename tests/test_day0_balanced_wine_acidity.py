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


class Day0BalancedWineAcidityTests(
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

    def test_serpent_agrees_with_acidity(
        self
    ):
        result = (
            self.scene
            .advance_to_balanced_acidity_idea()
        )

        event = result[
            "balance"
        ][
            "event"
        ]

        self.assertTrue(
            event[
                "agrees_acidity"
            ]
        )

    def test_serpent_says_too_much_acidity_is_bad(
        self
    ):
        result = (
            self.scene
            .advance_to_balanced_acidity_idea()
        )

        event = result[
            "balance"
        ][
            "event"
        ]

        self.assertEqual(
            event[
                "too_much_acidity"
            ],
            "bad"
        )

    def test_desired_acidity_becomes_moderate(
        self
    ):
        self.scene.advance_to_balanced_acidity_idea()

        hypothesis = (
            self.scene
            .serpent_lilith_good_drink_discussion[
                "current_hypothesis"
            ]
        )

        self.assertEqual(
            hypothesis[
                "acidity"
            ],
            "moderate"
        )

    def test_other_wine_properties_remain_unchanged(
        self
    ):
        self.scene.advance_to_balanced_acidity_idea()

        hypothesis = (
            self.scene
            .serpent_lilith_good_drink_discussion[
                "current_hypothesis"
            ]
        )

        self.assertTrue(
            hypothesis[
                "fuller_flavor"
            ]
        )

        self.assertTrue(
            hypothesis[
                "sweetness"
            ]
        )

        self.assertFalse(
            hypothesis[
                "bitterness"
            ]
        )

    def test_god_still_has_not_tasted_wine(
        self
    ):
        self.scene.advance_to_balanced_acidity_idea()

        self.assertFalse(
            self.scene.god[
                "bar_state"
            ][
                "wine_order"
            ][
                "tasted"
            ]
        )

    def test_discussion_remains_unresolved(
        self
    ):
        self.scene.advance_to_balanced_acidity_idea()

        self.assertFalse(
            self.scene
            .serpent_lilith_good_drink_discussion[
                "resolved"
            ]
        )


if __name__ == "__main__":
    unittest.main()
