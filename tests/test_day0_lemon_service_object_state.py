import unittest

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift,
)
from genesis.day0_lemon_service_state import (
    BartenderLemonRestockResult,
    BartenderLemonRestockReturnedEvent,
    BartenderLemonReturnResult,
    BartenderReportsMissingLemonEvent,
    LilithPointsOutLemonTreeEvent,
    LilithVodkaWithLemonOrderResult,
)
from gods import Gods
from idea_entities import IdeaEntities
from library import Library
from meeting_place.bar_yard_event_state import (
    LemonPickedResult,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class Day0LemonServiceObjectStateTests(
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

    def test_lilith_lemon_order_result_is_object_only(
        self
    ):
        scene = self._scene()
        scene.advance_to_lilith_entry()

        result = (
            scene
            .lilith_orders_vodka_with_lemon()
        )

        self.assertIsInstance(
            result,
            LilithVodkaWithLemonOrderResult,
        )
        self.assertIs(
            result.order,
            scene.lilith_order,
        )
        self.assertEqual(
            result.bartender.destination,
            "bar_yard",
        )
        self._assert_object_only(
            result,
            "order",
        )

    def test_lilith_lemon_runtime_events_are_objects(
        self
    ):
        scene = self._scene()
        scene.advance_to_lilith_entry()

        scene.lilith_orders_vodka_with_lemon()

        missing = [
            event
            for event
            in scene.meeting_place.events
            if isinstance(
                event,
                BartenderReportsMissingLemonEvent,
            )
        ]

        pointed = [
            event
            for event
            in scene.meeting_place.events
            if isinstance(
                event,
                LilithPointsOutLemonTreeEvent,
            )
        ]

        self.assertEqual(
            len(missing),
            1,
        )
        self.assertEqual(
            len(pointed),
            1,
        )
        self._assert_object_only(
            missing[0],
            "guest",
        )
        self._assert_object_only(
            pointed[0],
            "tree",
        )

    def test_single_lemon_return_keeps_runtime_objects(
        self
    ):
        scene = self._scene()
        scene.advance_to_lilith_entry()
        scene.lilith_orders_vodka_with_lemon()

        result = (
            scene
            .bartender_returns_with_lemon()
        )

        self.assertIsInstance(
            result,
            BartenderLemonReturnResult,
        )
        self.assertIsInstance(
            result.picked,
            LemonPickedResult,
        )
        self.assertEqual(
            result.stock.shots,
            1,
        )
        self.assertEqual(
            result.returned.ingredient,
            "lemon",
        )
        self._assert_object_only(
            result,
            "picked",
        )

    def test_restock_keeps_typed_pick_results(
        self
    ):
        scene = self._scene()

        result = (
            scene
            .bartender_runs_to_yard_for_more_lemons(
                amount=6
            )
        )

        self.assertIsInstance(
            result,
            BartenderLemonRestockResult,
        )
        self.assertIsInstance(
            result.returned,
            BartenderLemonRestockReturnedEvent,
        )
        self.assertEqual(
            len(result.picked),
            6,
        )
        self.assertTrue(
            all(
                isinstance(
                    picked,
                    LemonPickedResult,
                )
                for picked
                in result.picked
            )
        )
        self.assertEqual(
            result.returned.amount,
            6,
        )
        self.assertEqual(
            result.stock.shots,
            6,
        )
        self._assert_object_only(
            result,
            "returned",
        )


if __name__ == "__main__":
    unittest.main()
