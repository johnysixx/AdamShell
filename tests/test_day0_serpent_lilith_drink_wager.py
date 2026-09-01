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


class Day0SerpentLilithDrinkWagerTests(
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

        self.library = Library(
            self.universe
        )

        self.gods = Gods(
            self.universe
        )

        self.idea_entities = IdeaEntities(
            self.universe
        )

        self.scene = Day0FirstBarShift(
            universe=self.universe,
            meeting_place=self.bar,
            library=self.library,
            gods=self.gods,
            idea_entities=self.idea_entities
        )

        self.scene.advance_to_lilith_entry()

        self.scene.lilith_orders_vodka_with_lemon()

        self.scene.serpent_and_lilith_begin_conversation()

    def test_serpent_dislikes_all_three_drinks(
        self
    ):
        result = (
            self.scene
            .serpent_and_lilith_taste_first_drinks()
        )

        self.assertEqual(
            result[
                "serpent_reaction"
            ],
            {
                "wine": "dislikes",
                "beer": "dislikes",
                "mead": "dislikes"
            }
        )

    def test_lilith_tastes_serpents_drinks_and_dislikes_them_too(
        self
    ):
        result = (
            self.scene
            .serpent_and_lilith_taste_first_drinks()
        )

        self.assertEqual(
            result[
                "offered_by"
            ],
            "serpent"
        )

        self.assertEqual(
            result[
                "shared_with"
            ],
            "lilith"
        )

        self.assertEqual(
            result[
                "lilith_reaction"
            ],
            {
                "wine": "dislikes",
                "beer": "dislikes",
                "mead": "dislikes"
            }
        )

    def test_they_recognize_these_are_only_existing_examples(
        self
    ):
        self.scene.serpent_and_lilith_taste_first_drinks()

        wager = (
            self.scene
            .serpent_proposes_drink_wager_to_lilith()
        )

        self.assertFalse(
            wager[
                "challenge"
            ][
                "existing_better_example"
            ]
        )

        self.assertEqual(
            wager[
                "challenge"
            ][
                "eligible_drinks"
            ],
            [
                "wine",
                "beer",
                "mead"
            ]
        )

    def test_serpent_proposes_loser_pays_winners_bar_tabs(
        self
    ):
        self.scene.serpent_and_lilith_taste_first_drinks()

        wager = (
            self.scene
            .serpent_proposes_drink_wager_to_lilith()
        )

        self.assertEqual(
            wager[
                "proposed_by"
            ],
            "serpent"
        )

        self.assertEqual(
            wager[
                "stakes"
            ][
                "loser"
            ],
            "pays_winners_bar_tabs"
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

    def test_lilith_accepts_wager(
        self
    ):
        self.scene.serpent_and_lilith_taste_first_drinks()

        self.scene.serpent_proposes_drink_wager_to_lilith()

        wager = (
            self.scene
            .lilith_accepts_drink_wager()
        )

        self.assertTrue(
            wager[
                "accepted"
            ]
        )

        self.assertEqual(
            wager[
                "accepted_by"
            ],
            "lilith"
        )

        self.assertFalse(
            wager[
                "resolved"
            ]
        )

    def test_conversation_records_the_agreement(
        self
    ):
        self.scene.play_serpent_lilith_first_conversation()

        content = (
            self.scene
            .serpent_lilith_conversation
            .content
        )

        meanings = [
            item.meaning
            for item in content
        ]

        self.assertEqual(
            meanings,
            [
                (
                    "none_of_the_existing_wine_beer_or_mead_"
                    "tastes_good"
                ),
                "agrees",
                "proposes_drink_wager",
                "accepts_drink_wager"
            ]
        )


if __name__ == "__main__":
    unittest.main()
