import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_exploration_planner import (
    CatExplorationPlanner
)


class CatExplorationPlannerTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="explorer",
            color="black",
            fur_length="short"
        )

        self.cat["current_layer"] = (
            "meeting_place"
        )

        self.cat["position"] = {
            "x": 1.0,
            "y": 2.0,
            "z": 3.0
        }

    def test_default_target_from_meeting_place_is_quantum(
        self
    ):
        result = (
            CatExplorationPlanner
            .choose_destination(
                cat=self.cat,
                universe=self.universe
            )
        )

        self.assertTrue(
            result["selected"]
        )

        self.assertEqual(
            result["layer"],
            "quantum_layer"
        )

    def test_explicit_goal_has_priority(
        self
    ):
        self.cat["exploration_goal"] = {
            "layer": "eden",
            "position": {
                "x": 9.0,
                "y": 8.0,
                "z": 7.0
            }
        }

        result = (
            CatExplorationPlanner
            .choose_destination(
                cat=self.cat,
                universe=self.universe
            )
        )

        self.assertEqual(
            result["layer"],
            "eden"
        )

        self.assertEqual(
            result["position"],
            {
                "x": 9.0,
                "y": 8.0,
                "z": 7.0
            }
        )

    def test_positive_memory_makes_layer_attractive(
        self
    ):
        self.cat["memory"].remember(
            event_type="successful_exploration",
            location={
                "x": 4.0,
                "y": 5.0,
                "z": 6.0
            },
            details={
                "target_layer": "history"
            }
        )

        result = (
            CatExplorationPlanner
            .choose_destination(
                cat=self.cat,
                universe=self.universe
            )
        )

        history = next(
            candidate
            for candidate in result[
                "candidates"
            ]
            if candidate["layer"]
            == "history"
        )

        self.assertIn(
            "positive_memory",
            history["reasons"]
        )

    def test_dangerous_memory_reduces_score(
        self
    ):
        self.cat["memory"].remember(
            event_type="dangerous_location",
            location={
                "x": 4.0,
                "y": 0.0,
                "z": 0.0
            },
            details={
                "target_layer": "history"
            }
        )

        result = (
            CatExplorationPlanner
            .choose_destination(
                cat=self.cat,
                universe=self.universe
            )
        )

        history = next(
            candidate
            for candidate in result[
                "candidates"
            ]
            if candidate["layer"]
            == "history"
        )

        self.assertIn(
            "dangerous_memory",
            history["reasons"]
        )

    def test_quantum_cat_can_choose_meeting_place(
        self
    ):
        self.cat["current_layer"] = (
            "quantum_layer"
        )

        result = (
            CatExplorationPlanner
            .choose_destination(
                cat=self.cat,
                universe=self.universe
            )
        )

        self.assertTrue(
            result["selected"]
        )

        self.assertNotEqual(
            result["layer"],
            "quantum_layer"
        )


if __name__ == "__main__":
    unittest.main()