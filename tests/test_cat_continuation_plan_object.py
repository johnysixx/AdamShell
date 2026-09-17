import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_exploration_planner import (
    CatExplorationPlanner
)
from cats.cat_exploration_state import (
    CatContinuationCandidate,
    CatContinuationPlan,
)


class CatContinuationPlanObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="continuation_cat",
            color="black",
            fur_length="short",
        )

        self.cat.current_layer = (
            "quantum_layer"
        )

        self.cat.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

    def plan(self):
        return (
            CatExplorationPlanner
            .choose_continuation_destination(
                cat=self.cat,
                universe=self.universe,
            )
        )

    def test_continuation_plan_is_object(
        self
    ):
        plan = self.plan()

        self.assertIsInstance(
            plan,
            CatContinuationPlan,
        )

        self.assertTrue(
            plan.selected
        )

        self.assertEqual(
            plan.reason,
            "continue_quantum_exploration",
        )

        self.assertFalse(
            hasattr(
                plan,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                plan,
                "__getitem__",
            )
        )

    def test_continuation_candidates_are_objects(
        self
    ):
        plan = self.plan()

        self.assertEqual(
            len(
                plan.candidates
            ),
            6,
        )

        self.assertTrue(
            all(
                isinstance(
                    candidate,
                    CatContinuationCandidate,
                )
                for candidate
                in plan.candidates
            )
        )

        self.assertTrue(
            all(
                not hasattr(
                    candidate,
                    "get",
                )
                for candidate
                in plan.candidates
            )
        )

    def test_equal_scores_keep_first_direction_first(
        self
    ):
        plan = self.plan()

        winner = plan.candidates[0]

        self.assertEqual(
            winner.direction_index,
            0,
        )

        self.assertEqual(
            plan.position,
            winner.position,
        )

        self.assertEqual(
            plan.score,
            winner.score,
        )


if __name__ == "__main__":
    unittest.main()
