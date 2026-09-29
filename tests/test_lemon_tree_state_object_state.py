import unittest

from meeting_place.bar_yard import BarYard
from meeting_place.lemon_tree_state import LemonTreeState


class LemonTreeStateObjectStateTests(
    unittest.TestCase
):

    def test_tree_starts_fruiting_as_enum(self):
        tree = BarYard().lemon_tree

        self.assertIs(
            tree.state,
            LemonTreeState.FRUITING,
        )
        self.assertEqual(
            tree.to_dict()["state"],
            "fruiting",
        )

    def test_last_lemon_strips_tree(self):
        yard = BarYard()
        yard.lemon_tree.lemons = 1

        yard.pick_lemon("tester")

        self.assertIs(
            yard.lemon_tree.state,
            LemonTreeState.STRIPPED,
        )

    def test_first_month_enters_flowering_state(self):
        yard = BarYard()
        yard.lemon_tree.lemons = 1
        yard.pick_lemon("tester")

        result = yard.advance_month()

        self.assertIs(
            yard.lemon_tree.state,
            LemonTreeState.FLOWERING,
        )
        self.assertEqual(
            result["state"],
            "flowering",
        )

    def test_sixth_month_returns_to_fruiting_state(self):
        yard = BarYard()
        yard.lemon_tree.lemons = 1
        yard.pick_lemon("tester")

        result = None

        for _ in range(6):
            result = yard.advance_month()

        self.assertIs(
            yard.lemon_tree.state,
            LemonTreeState.FRUITING,
        )
        self.assertEqual(
            result["state"],
            "fruiting",
        )

    def test_string_state_is_rejected(self):
        tree = BarYard().lemon_tree

        with self.assertRaises(TypeError):
            tree.state = "flowering"

    def test_state_values_define_domain_names(self):
        self.assertEqual(
            {
                state.value
                for state in LemonTreeState
            },
            {
                "fruiting",
                "stripped",
                "flowering",
            },
        )


if __name__ == "__main__":
    unittest.main()
