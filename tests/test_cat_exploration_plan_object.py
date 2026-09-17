import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_exploration_planner import (
    CatExplorationPlanner
)
from cats.cat_exploration_state import (
    CatExplorationCandidate,
    CatExplorationPlan,
)


class CatExplorationPlanObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="exploration_object_cat",
            color="black",
            fur_length="short",
        )

        self.cat.current_layer = (
            "meeting_place"
        )

    def plan(self):
        return (
            CatExplorationPlanner
            .choose_destination(
                cat=self.cat,
                universe=self.universe,
            )
        )

    def test_plan_is_object(
        self
    ):
        plan = self.plan()

        self.assertIsInstance(
            plan,
            CatExplorationPlan,
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

    def test_candidates_are_objects(
        self
    ):
        plan = self.plan()

        self.assertGreater(
            len(
                plan.candidates
            ),
            0,
        )

        self.assertTrue(
            all(
                isinstance(
                    candidate,
                    CatExplorationCandidate,
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

    def test_candidate_scorer_rejects_mapping(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            (
                CatExplorationPlanner
                ._score_candidate(
                    cat=self.cat,
                    candidate={
                        "layer":
                            "quantum_layer",
                    },
                )
            )


if __name__ == "__main__":
    unittest.main()
