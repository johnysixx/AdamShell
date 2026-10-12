import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_god_wine_service_state import (
    BartenderServesGodWineEvent,
    GodOrdersWineToJudgeDiscussionEvent,
    GodWineServiceResult,
    SerpentGrimacesAtLilithEvent,
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
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0GodWineServiceObjectStateTests(
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

    def test_grimace_event_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_acidity_wine_idea()

        event = (
            scene
            .serpent_grimaces_at_lilith_and_turns_to_god()
        )

        self.assertIsInstance(
            event,
            SerpentGrimacesAtLilithEvent,
        )

        self.assertEqual(
            event.reaction,
            "grimace",
        )

        self.assertEqual(
            event.turns_to,
            "god",
        )

        self._assert_object_only(
            event,
            "reaction",
        )

    def test_wine_order_event_is_object_only(
        self
    ):
        scene = self._scene()

        scene.advance_to_acidity_wine_idea()

        scene.serpent_grimaces_at_lilith_and_turns_to_god()

        event = (
            scene
            .god_orders_wine_to_judge_discussion()
        )

        self.assertIsInstance(
            event,
            GodOrdersWineToJudgeDiscussionEvent,
        )

        self.assertEqual(
            event.drink,
            "wine",
        )

        self.assertEqual(
            event.purpose,
            "judge_wine_discussion",
        )

        self._assert_object_only(
            event,
            "drink",
        )

    def test_wine_service_result_is_object_only(
        self
    ):
        scene = self._scene()

        result = (
            scene.advance_to_god_receives_wine()
        )

        service = result[
            "service"
        ]

        self.assertIsInstance(
            service,
            GodWineServiceResult,
        )

        self.assertIsInstance(
            service.drink,
            BarDrink,
        )

        self.assertIsInstance(
            service.receipt,
            BarReceiptState,
        )

        self.assertIsInstance(
            service.event,
            BartenderServesGodWineEvent,
        )

        self.assertFalse(
            service.event.tasted
        )

        self.assertFalse(
            service.receipt.paid
        )

        self.assertIs(
            scene.god.bar_state
            .wine_order
            .final_drink,
            service.drink,
        )

        self._assert_object_only(
            service,
            "drink",
        )

        self._assert_object_only(
            service.event,
            "tasted",
        )


if __name__ == "__main__":
    unittest.main()
