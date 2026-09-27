import unittest

from cats.cat_navigation_decision import (
    CatNavigationDecision,
)


class CatNavigationDecisionEnumObjectStateTests(
    unittest.TestCase
):

    def test_decision_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                decision.value
                for decision
                in CatNavigationDecision
            },
            {
                "accepted",
                "declined",
            },
        )


if __name__ == "__main__":
    unittest.main()
