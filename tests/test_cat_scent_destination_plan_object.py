from core.entity.components import SpatialVector3
import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge
from cats.cat_exploration_planner import (
    CatExplorationPlanner
)
from cats.cat_exploration_state import (
    CatScentDestinationCandidate,
    CatScentDestinationPlan,
)


class CatScentDestinationPlanObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="scent_plan_cat",
            color="black",
            fur_length="short",
        )

        self.cat.current_layer = (
            "quantum_layer"
        )

    def remember_scent(self):
        CatKnowledge.remember_scent_place(
            cat=self.cat,
            layer="quantum_layer",
            position=SpatialVector3(x=5.0, y=0.0, z=0.0),
            source_id="test_trace",
            recognized_identity="cat:pazuzu",
            components={
                "cat": 1.0,
            },
            perceived_intensity=0.8,
            universe_tick=10,
        )

    def test_scent_destination_is_object(
        self
    ):
        self.remember_scent()

        plan = (
            CatExplorationPlanner
            .choose_scent_destination(
                cat=self.cat,
                preferred_identity="cat:pazuzu",
            )
        )

        self.assertIsInstance(
            plan,
            CatScentDestinationPlan,
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

    def test_scent_candidates_are_objects(
        self
    ):
        self.remember_scent()

        plan = (
            CatExplorationPlanner
            .choose_scent_destination(
                cat=self.cat,
                preferred_identity="cat:pazuzu",
            )
        )

        self.assertTrue(
            plan.candidates
        )

        self.assertTrue(
            all(
                isinstance(
                    candidate,
                    CatScentDestinationCandidate,
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

    def test_missing_scent_returns_object_failure_plan(
        self
    ):
        plan = (
            CatExplorationPlanner
            .choose_scent_destination(
                cat=self.cat,
            )
        )

        self.assertIsInstance(
            plan,
            CatScentDestinationPlan,
        )

        self.assertFalse(
            plan.selected
        )

        self.assertEqual(
            plan.reason,
            "no_known_scent_places",
        )

        self.assertEqual(
            plan.candidates,
            [],
        )


if __name__ == "__main__":
    unittest.main()
