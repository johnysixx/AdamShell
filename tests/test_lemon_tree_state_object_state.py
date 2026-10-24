import unittest

from meeting_place.bar_yard import (
    BarYard,
)
from meeting_place.bar_yard_event_state import (
    LemonNotFoundResult,
    LemonPickedResult,
    LemonTreeBeginsFloweringEvent,
    LemonTreeMonthPassedResult,
    LemonTreeNewCropEvent,
)
from meeting_place.lemon_tree_state import (
    LemonTreeState,
)


class LemonTreeStateObjectStateTests(
    unittest.TestCase
):

    def assert_not_mapping(
        self,
        state,
        key,
    ):
        for name in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
            "__getitem__",
            "__setitem__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    state,
                    name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = state[
                key
            ]

    def test_tree_starts_fruiting_as_enum(
        self
    ):
        tree = (
            BarYard()
            .lemon_tree
        )

        self.assertIs(
            tree.state,
            LemonTreeState.FRUITING,
        )

        self.assertEqual(
            tree.to_dict()["state"],
            "fruiting",
        )

    def test_last_lemon_strips_tree(
        self
    ):
        yard = BarYard()

        yard.lemon_tree.lemons = 1

        yard.pick_lemon(
            "tester"
        )

        self.assertIs(
            yard.lemon_tree.state,
            LemonTreeState.STRIPPED,
        )

    def test_first_month_enters_flowering_state(
        self
    ):
        yard = BarYard()

        yard.lemon_tree.lemons = 1

        yard.pick_lemon(
            "tester"
        )

        result = (
            yard.advance_month()
        )

        self.assertIsInstance(
            result,
            LemonTreeMonthPassedResult,
        )

        self.assertIs(
            result.state,
            LemonTreeState.FLOWERING,
        )

        self.assertEqual(
            result.state.value,
            "flowering",
        )

    def test_sixth_month_returns_to_fruiting_state(
        self
    ):
        yard = BarYard()

        yard.lemon_tree.lemons = 1

        yard.pick_lemon(
            "tester"
        )

        result = None

        for _ in range(6):
            result = (
                yard.advance_month()
            )

        self.assertIsInstance(
            result,
            LemonTreeMonthPassedResult,
        )

        self.assertIs(
            yard.lemon_tree.state,
            LemonTreeState.FRUITING,
        )

        self.assertIs(
            result.state,
            LemonTreeState.FRUITING,
        )

        self.assertEqual(
            result.state.value,
            "fruiting",
        )

    def test_string_state_is_rejected(
        self
    ):
        tree = (
            BarYard()
            .lemon_tree
        )

        with self.assertRaises(
            TypeError
        ):
            tree.state = "flowering"

    def test_state_values_define_domain_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state
                in LemonTreeState
            },
            {
                "fruiting",
                "stripped",
                "flowering",
            },
        )

    def test_lemon_pick_result_is_object_state(
        self
    ):
        yard = BarYard()

        result = yard.pick_lemon(
            "tester"
        )

        self.assertIsInstance(
            result,
            LemonPickedResult,
        )

        self.assertTrue(
            result.picked
        )

        self.assertEqual(
            result.picker,
            "tester",
        )

        self.assertEqual(
            result.fruit,
            "lemon",
        )

        self.assertEqual(
            result.source,
            "lemon_tree",
        )

        self.assertEqual(
            result.lemons_remaining,
            6,
        )

        self.assert_not_mapping(
            result,
            "picked",
        )

        self.assertEqual(
            result.name,
            "lemon_picked",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

    def test_lemon_not_found_result_is_object_state(
        self
    ):
        yard = BarYard()

        yard.lemon_tree.lemons = 0
        yard.lemon_tree.has_lemons = False

        result = yard.pick_lemon(
            "tester"
        )

        self.assertIsInstance(
            result,
            LemonNotFoundResult,
        )

        self.assertFalse(
            result.picked
        )

        self.assertEqual(
            result.lemons_remaining,
            0,
        )

        self.assert_not_mapping(
            result,
            "picked",
        )

    def test_lemon_tree_lifecycle_events_are_objects(
        self
    ):
        yard = BarYard()

        yard.lemon_tree.lemons = 1

        yard.pick_lemon(
            "tester"
        )

        flowering = (
            yard.advance_month()
        )

        self.assertIsInstance(
            flowering.events[0],
            LemonTreeBeginsFloweringEvent,
        )

        self.assertEqual(
            flowering.events[0].month,
            1,
        )

        self.assertEqual(
            flowering.events[0].flowers,
            12,
        )

        self.assert_not_mapping(
            flowering.events[0],
            "name",
        )

        result = flowering

        for _ in range(5):
            result = (
                yard.advance_month()
            )

        crop = result.events[-1]

        self.assertIsInstance(
            crop,
            LemonTreeNewCropEvent,
        )

        self.assertEqual(
            crop.lemons,
            7,
        )

        self.assert_not_mapping(
            crop,
            "name",
        )

        self.assert_not_mapping(
            result,
            "state",
        )


if __name__ == "__main__":
    unittest.main()
