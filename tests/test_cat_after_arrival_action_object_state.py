import unittest

from cats.cat_after_arrival_action import (
    CatAfterArrivalAction,
)


class CatAfterArrivalActionObjectStateTests(
    unittest.TestCase
):

    def test_action_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                action.value
                for action
                in CatAfterArrivalAction
            },
            {
                "continue_exploration",
                "rest_at_destination",
                "return_via_exploration_pair",
            },
        )


if __name__ == "__main__":
    unittest.main()
