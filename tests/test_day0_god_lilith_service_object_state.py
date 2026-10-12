import unittest

from core.entity.cronenberg import Cronenberg
from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_god_lilith_service_state import (
    BartenderMixesGodsLilithEvent,
    BartenderServesGodsLilithEvent,
    GodsLilithFailureResult,
    GodsLilithFailsWithoutLemonEvent,
    GodsLilithServiceResult,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_objects import BarDrink
from meeting_place.bar_receipt_state import (
    BarReceiptState,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0GodLilithServiceObjectStateTests(
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

    def test_missing_lemon_failure_is_typed(
        self
    ):
        scene = self._scene()

        scene.advance_to_third_wine_idea()

        result = (
            scene
            .bartender_attempts_gods_lilith_without_lemon()
        )

        self.assertIsInstance(
            result,
            GodsLilithFailureResult,
        )

        self.assertIsInstance(
            result.event,
            GodsLilithFailsWithoutLemonEvent,
        )

        self.assertIsInstance(
            result.cronenberg,
            Cronenberg,
        )

        self.assertTrue(
            result.event.cronenberg_created
        )

        self._assert_object_only(
            result,
            "event",
        )

        self._assert_object_only(
            result.event,
            "reason",
        )

    def test_successful_mix_emits_typed_event(
        self
    ):
        scene = self._scene()

        scene.advance_to_lemon_restock_after_god_order()

        drink = (
            scene
            .bartender_mixes_gods_lilith_after_restock()
        )

        event = (
            scene.meeting_place.events[-1]
        )

        self.assertIsInstance(
            drink,
            BarDrink,
        )

        self.assertIsInstance(
            event,
            BartenderMixesGodsLilithEvent,
        )

        self.assertEqual(
            event.sugar_cubes_used,
            2,
        )

        self.assertEqual(
            event.lemons_remaining,
            5,
        )

        self._assert_object_only(
            event,
            "lemons_remaining",
        )

    def test_service_result_is_typed(
        self
    ):
        scene = self._scene()

        scene.advance_to_lemon_restock_after_god_order()

        scene.bartender_mixes_gods_lilith_after_restock()

        result = (
            scene
            .bartender_serves_gods_lilith_with_receipt()
        )

        event = (
            scene.meeting_place.events[-1]
        )

        self.assertIsInstance(
            result,
            GodsLilithServiceResult,
        )

        self.assertIsInstance(
            result.drink,
            BarDrink,
        )

        self.assertIsInstance(
            result.receipt,
            BarReceiptState,
        )

        self.assertIsInstance(
            event,
            BartenderServesGodsLilithEvent,
        )

        self.assertFalse(
            result.receipt.paid
        )

        self.assertEqual(
            result.receipt.status,
            "open_unpaid",
        )

        self._assert_object_only(
            result,
            "receipt",
        )

        self._assert_object_only(
            event,
            "receipt_number",
        )


if __name__ == "__main__":
    unittest.main()
