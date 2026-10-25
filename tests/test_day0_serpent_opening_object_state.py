import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_serpent_opening_state import (
    SerpentBetProposalResult,
    SerpentFirstDrinksServiceResult,
    SerpentOrdersFirstDrinksEvent,
    SerpentProposesBetEvent,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import (
    BarDrink,
)
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)
from meeting_place.bartender_event_state import (
    BartenderRefusedBetEvent,
    BartenderShiftAlreadyActiveResult,
    BartenderShiftStartedEvent,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0SerpentOpeningObjectStateTests(
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

    def test_shift_start_returns_real_event(
        self
    ):
        scene = self._scene()

        event = scene.start_shift()

        self.assertIsInstance(
            event,
            BartenderShiftStartedEvent,
        )

        self.assertIs(
            event,
            scene.meeting_place
            .bartender
            .event_memory[-1],
        )

        self._assert_object_only(
            event,
            "name",
        )

    def test_repeated_shift_start_is_object_result(
        self
    ):
        scene = self._scene()

        scene.start_shift()

        result = scene.start_shift()

        self.assertIsInstance(
            result,
            BartenderShiftAlreadyActiveResult,
        )

        self._assert_object_only(
            result,
            "bar_day",
        )

    def test_first_drinks_result_is_object_graph(
        self
    ):
        scene = self._scene()

        scene.start_shift()
        scene.serpent_is_born_and_enters()

        result = (
            scene
            .serpent_orders_first_drinks()
        )

        self.assertIsInstance(
            result,
            SerpentFirstDrinksServiceResult,
        )

        self.assertIsInstance(
            result.drinks,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    drink,
                    BarDrink,
                )
                for drink in result.drinks
            )
        )

        self.assertEqual(
            tuple(
                drink.name
                for drink in result.drinks
            ),
            (
                "wine",
                "beer",
                "mead",
            ),
        )

        self.assertIsInstance(
            result.receipt,
            BarReceiptState,
        )

        self.assertIsNone(
            result.payment
        )

        self.assertEqual(
            result.tab_status,
            "open",
        )

        self.assertIsInstance(
            result.event,
            SerpentOrdersFirstDrinksEvent,
        )

        self.assertFalse(
            hasattr(
                SerpentFirstDrinksServiceResult,
                "from_mapping",
            )
        )

        self._assert_object_only(
            result,
            "drinks",
        )

        self._assert_object_only(
            result.event,
            "drinks",
        )

    def test_bet_result_uses_real_bartender_event(
        self
    ):
        scene = self._scene()

        scene.start_shift()
        scene.serpent_is_born_and_enters()
        scene.serpent_orders_first_drinks()

        result = (
            scene.serpent_proposes_bet()
        )

        self.assertIsInstance(
            result,
            SerpentBetProposalResult,
        )

        self.assertIsInstance(
            result.proposal,
            SerpentProposesBetEvent,
        )

        self.assertIsInstance(
            result.response,
            BartenderRefusedBetEvent,
        )

        self.assertIs(
            result.response,
            scene.meeting_place
            .bartender
            .event_memory[-1],
        )

        self.assertFalse(
            result.response.accepted
        )

        self.assertTrue(
            scene.serpent
            .bar_state
            .bet
            .offered
        )

        self.assertFalse(
            scene.serpent
            .bar_state
            .bet
            .accepted
        )

        self._assert_object_only(
            result,
            "response",
        )

        self._assert_object_only(
            result.proposal,
            "target",
        )

        self._assert_object_only(
            result.response,
            "accepted",
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        scene = self._scene()

        scene.start_shift()
        scene.serpent_is_born_and_enters()
        scene.serpent_orders_first_drinks()
        scene.serpent_proposes_bet()

        names = [
            event["name"]
            for event
            in scene.history
        ]

        self.assertEqual(
            names,
            [
                "bartender_shift_started",
                "serpent_born",
                "serpent_entered_bar",
                "serpent_orders_wine_beer_and_mead",
                "serpent_proposes_bet",
                "bartender_refused_bet",
            ],
        )

        self.assertTrue(
            all(
                isinstance(
                    event,
                    dict,
                )
                for event
                in scene.history
            )
        )


if __name__ == "__main__":
    unittest.main()
