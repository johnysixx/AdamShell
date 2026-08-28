import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import (
    MeetingPlace
)
from library import Library
from gods import Gods
from idea_entities import IdeaEntities
from genesis.day0_first_bar_shift import (
    Day0FirstBarShift
)


class Day0FirstBarShiftTests(
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

        self.idea_entities = (
            IdeaEntities(
                self.universe
            )
        )

        self.scene = (
            Day0FirstBarShift(
                universe=self.universe,
                meeting_place=self.bar,
                library=self.library,
                gods=self.gods,
                idea_entities=(
                    self.idea_entities
                )
            )
        )

    def test_shift_exists_before_first_guest(
        self
    ):
        self.scene.start_shift()

        self.assertTrue(
            self.bar.bartender.shift_active
        )

        self.assertEqual(
            self.bar.entities,
            []
        )

    def test_serpent_arrives_at_0420_bar_time(
        self
    ):
        self.scene.start_shift()

        self.scene.serpent_is_born_and_enters()

        self.assertEqual(
            self.bar.bar_clock.hour,
            4
        )

        self.assertEqual(
            self.bar.bar_clock.minute,
            20
        )

        self.assertEqual(
            self.bar.bar_clock.time_text,
            "04:20"
        )

        arrival = next(
            event
            for event
            in self.scene.history
            if event.get(
                "name"
            )
            == "serpent_entered_bar"
        )

        self.assertEqual(
            arrival[
                "bar_time"
            ],
            "04:20"
        )

    def test_serpent_has_three_drinks_and_unpaid_tab(
        self
    ):
        self.scene.start_shift()
        self.scene.serpent_is_born_and_enters()

        result = (
            self.scene
            .serpent_orders_first_drinks()
        )

        self.assertEqual(
            [
                drink["name"]
                for drink
                in result["drinks"]
            ],
            [
                "wine",
                "beer",
                "mead"
            ]
        )

        self.assertIsNone(
            result["payment"]
        )

        self.assertFalse(
            result["receipt"]["paid"]
        )

        self.assertEqual(
            result["receipt"]["status"],
            "open_unpaid"
        )

    def test_bartender_refuses_serpent_bet(
        self
    ):
        self.scene.start_shift()
        self.scene.serpent_is_born_and_enters()
        self.scene.serpent_orders_first_drinks()

        result = (
            self.scene
            .serpent_proposes_bet()
        )

        self.assertFalse(
            result[
                "response"
            ][
                "accepted"
            ]
        )

    def test_requested_checkpoint(
        self
    ):
        state = (
            self.scene
            .advance_to_lilith_entry()
        )

        self.assertTrue(
            state[
                "shift_active"
            ]
        )

        self.assertTrue(
            state[
                "serpent"
            ][
                "in_bar"
            ]
        )

        self.assertEqual(
            state[
                "serpent"
            ][
                "bar_state"
            ][
                "activity"
            ],
            "tasting_ordered_drinks"
        )

        self.assertFalse(
            state[
                "serpent"
            ][
                "tab"
            ][
                "paid"
            ]
        )

        self.assertTrue(
            state[
                "god"
            ][
                "in_library"
            ]
        )

        self.assertEqual(
            state[
                "god"
            ][
                "role"
            ],
            "librarian"
        )

        self.assertIsNone(
            state[
                "god"
            ][
                "book"
            ][
                "title"
            ]
        )

        self.assertEqual(
            state[
                "god"
            ][
                "book"
            ][
                "state"
            ],
            "being_written"
        )

        self.assertTrue(
            state[
                "lilith"
            ][
                "in_bar"
            ]
        )

        history_names = [
            event["name"]
            for event
            in state[
                "history"
            ]
        ]

        self.assertLess(
            history_names.index(
                "bartender_shift_started"
            ),
            history_names.index(
                "serpent_born"
            )
        )

        self.assertLess(
            history_names.index(
                "serpent_born"
            ),
            history_names.index(
                "god_born"
            )
        )

        self.assertLess(
            history_names.index(
                "god_begins_first_unnamed_book"
            ),
            history_names.index(
                "lilith_born"
            )
        )


    def test_canonical_lilith_entry_checkpoint(
        self
    ):
        state = (
            self.scene
            .advance_to_lilith_entry()
        )

        # ----------------------------------------------------
        # BAR TIME
        # ----------------------------------------------------

        self.assertEqual(
            self.bar.bar_clock.time_text,
            "04:20"
        )

        self.assertTrue(
            state[
                "shift_active"
            ]
        )

        # ----------------------------------------------------
        # SERPENT
        # ----------------------------------------------------

        serpent = self.scene.serpent

        self.assertIsNotNone(
            serpent
        )

        self.assertIn(
            serpent,
            self.bar.entities
        )

        self.assertEqual(
            serpent[
                "bar_state"
            ][
                "seat"
            ],
            "at_bar"
        )

        self.assertEqual(
            serpent[
                "bar_state"
            ][
                "activity"
            ],
            "tasting_ordered_drinks"
        )

        self.assertEqual(
            serpent[
                "bar_state"
            ][
                "drinks"
            ],
            [
                "wine",
                "beer",
                "mead"
            ]
        )

        self.assertEqual(
            serpent[
                "bar_state"
            ][
                "tab"
            ],
            "open"
        )

        self.assertFalse(
            serpent[
                "bar_state"
            ][
                "paid"
            ]
        )

        self.assertTrue(
            serpent[
                "bar_state"
            ][
                "bet"
            ][
                "offered"
            ]
        )

        self.assertFalse(
            serpent[
                "bar_state"
            ][
                "bet"
            ][
                "accepted"
            ]
        )

        tab = (
            self.bar
            .bar_counter
            .cash_register
            .open_tabs[
                "serpent"
            ]
        )

        self.assertEqual(
            tab[
                "status"
            ],
            "open"
        )

        self.assertFalse(
            tab[
                "paid"
            ]
        )

        self.assertEqual(
            [
                item[
                    "drink"
                ]
                for item
                in tab[
                    "items"
                ]
            ],
            [
                "wine",
                "beer",
                "mead"
            ]
        )

        self.assertEqual(
            len(
                self.bar
                .bar_counter
                .cash_register
                .receipts
            ),
            1
        )

        receipt = (
            self.bar
            .bar_counter
            .cash_register
            .receipts[
                0
            ]
        )

        self.assertEqual(
            receipt[
                "status"
            ],
            "open_unpaid"
        )

        self.assertFalse(
            receipt[
                "paid"
            ]
        )

        self.assertIsNone(
            receipt[
                "payment"
            ]
        )

        # ----------------------------------------------------
        # GOD + LIBRARY
        # ----------------------------------------------------

        god = self.scene.god

        self.assertIsNotNone(
            god
        )

        self.assertEqual(
            god[
                "role"
            ],
            "librarian"
        )

        self.assertTrue(
            self.library.god_present
        )

        self.assertNotIn(
            god,
            self.bar.entities
        )

        book = (
            self.scene.first_book
        )

        self.assertIsNotNone(
            book
        )

        self.assertIsNone(
            book[
                "title"
            ]
        )

        self.assertEqual(
            book[
                "state"
            ],
            "being_written"
        )

        self.assertEqual(
            book[
                "location"
            ],
            "library_with_author"
        )

        # ----------------------------------------------------
        # LILITH
        # ----------------------------------------------------

        lilith = self.scene.lilith

        self.assertIsNotNone(
            lilith
        )

        self.assertIn(
            lilith,
            self.bar.entities
        )

        self.assertEqual(
            lilith[
                "type"
            ],
            "idea_entity"
        )

        self.assertEqual(
            lilith[
                "principle"
            ][
                "name"
            ],
            "feminine_principle"
        )

        # Lilith has only entered.
        # No encounter with God has happened yet.
        self.assertNotIn(
            "met_god",
            lilith
        )

        self.assertNotIn(
            "god",
            lilith.get(
                "knowledge",
                {}
            )
        )

        # ----------------------------------------------------
        # ORDER OF HISTORY
        # ----------------------------------------------------

        names = [
            event[
                "name"
            ]
            for event
            in state[
                "history"
            ]
        ]

        expected_order = [
            "bartender_shift_started",
            "serpent_born",
            "serpent_entered_bar",
            "serpent_orders_wine_beer_and_mead",
            "serpent_proposes_bet",
            "bartender_refused_bet",
            "god_born",
            "god_entered_library",
            "god_begins_first_unnamed_book",
            "lilith_born",
            "lilith_entered_bar"
        ]

        self.assertEqual(
            names,
            expected_order
        )

        # ----------------------------------------------------
        # CHECKPOINT MUST CONTAIN EXACTLY TWO BAR GUESTS
        # ----------------------------------------------------

        self.assertEqual(
            len(
                self.bar.entities
            ),
            2
        )

        self.assertIs(
            self.bar.entities[
                0
            ],
            serpent
        )

        self.assertIs(
            self.bar.entities[
                1
            ],
            lilith
        )


if __name__ == "__main__":
    unittest.main()
