from core.entity.components import SpatialVector3
import unittest
from types import SimpleNamespace

from cats.cat_exploration_goal import (
    CatExplorationGoal,
)
from cats.cat_exploration_planner import (
    CatExplorationPlanner,
)


class CatExplorationGoalObjectStateTests(
    unittest.TestCase
):

    def test_goal_has_no_mapping_api(
        self
    ):
        goal = CatExplorationGoal(
            layer='quantum_layer',
            position=SpatialVector3(x=1.0, y=2.0, z=3.0),
        )

        self.assertEqual(
            goal.layer,
            'quantum_layer',
        )

        self.assertEqual(
            goal.position,
            SpatialVector3(x=1.0, y=2.0, z=3.0),
        )

        self.assertFalse(
            hasattr(
                goal,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                goal,
                '__getitem__',
            )
        )

        self.assertFalse(
            hasattr(
                goal,
                '__setitem__',
            )
        )

    def test_planner_rejects_mapping_goal(
        self
    ):
        cat = SimpleNamespace(
            exploration_goal={
                'layer': 'quantum_layer',
                'position': {
                    'x': 1.0,
                    'y': 0.0,
                    'z': 0.0,
                },
            },
        )

        with self.assertRaises(
            TypeError
        ):
            CatExplorationPlanner.collect_candidates(
                cat=cat,
                universe=SimpleNamespace(),
            )

    def test_planner_rejects_scalar_goal(
        self
    ):
        cat = SimpleNamespace(
            exploration_goal='quantum_layer',
        )

        with self.assertRaises(
            TypeError
        ):
            CatExplorationPlanner.collect_candidates(
                cat=cat,
                universe=SimpleNamespace(),
            )


if __name__ == '__main__':
    unittest.main()
