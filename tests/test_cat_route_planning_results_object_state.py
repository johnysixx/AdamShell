import unittest

from core.entity.components import (
    SpatialVector3,
)
from core.entity.quantum_cat_route import (
    QuantumCatRoute,
)
from navigation import NavigationEngine
from navigation.navigation_result_state import (
    NavigationDirectRoutePlan,
    NavigationNearestTargetResult,
)
from universe.quantum_cat_navigation_result_state import (
    QuantumCatRouteNotPlannedResult,
    QuantumCatRoutePlannedResult,
)
from universe.universe import Universe


class Candidate:

    def __init__(
        self,
        name,
        position,
    ):
        self.name = name
        self.position = position


class CatRoutePlanningResultsObjectStateTests(
    unittest.TestCase
):

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
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
            _ = value[
                "name"
            ]

    def test_navigation_direct_route_is_object(
        self
    ):
        engine = NavigationEngine(
            default_step_size=2.0
        )

        result = engine.direct_route(
            SpatialVector3.zero(),
            SpatialVector3(
                x=3.0,
                y=4.0,
                z=0.0,
            ),
        )

        self.assertIsInstance(
            result,
            NavigationDirectRoutePlan,
        )

        self.assertAlmostEqual(
            result.distance,
            5.0,
        )

        self.assertEqual(
            result.step_count,
            3,
        )

        self.assertIsInstance(
            result.route_steps,
            tuple,
        )

        self.assertTrue(
            all(
                isinstance(
                    step,
                    SpatialVector3,
                )
                for step
                in result.route_steps
            )
        )

        self.assert_object_only(
            result
        )

    def test_nearest_target_is_object(
        self
    ):
        engine = NavigationEngine()

        near = Candidate(
            "near",
            SpatialVector3(
                x=1.0,
                y=0.0,
                z=0.0,
            ),
        )

        far = Candidate(
            "far",
            SpatialVector3(
                x=5.0,
                y=0.0,
                z=0.0,
            ),
        )

        result = engine.nearest_target(
            SpatialVector3.zero(),
            [
                far,
                near,
            ],
        )

        self.assertIsInstance(
            result,
            NavigationNearestTargetResult,
        )

        self.assertIs(
            result.target,
            near,
        )

        self.assertEqual(
            result.position,
            near.position,
        )

        self.assertAlmostEqual(
            result.distance,
            1.0,
        )

        self.assert_object_only(
            result
        )

    def test_nearest_target_none_is_not_mapping_sentinel(
        self
    ):
        engine = NavigationEngine()

        result = engine.nearest_target(
            SpatialVector3.zero(),
            [],
        )

        self.assertIsNone(
            result
        )

    def test_quantum_direct_cat_route_is_object(
        self
    ):
        universe = Universe()
        universe.enable_quantum_layer()

        result = (
            universe
            .quantum_space
            .plan_direct_cat_route(
                cat_id="object_route_cat",
                start_position=
                    SpatialVector3.zero(),
                destination_position=
                    SpatialVector3(
                        x=2.0,
                        y=0.0,
                        z=0.0,
                    ),
                destination="target",
                step_size=1.0,
            )
        )

        self.assertIsInstance(
            result,
            QuantumCatRoutePlannedResult,
        )

        self.assertIsInstance(
            result.plan,
            NavigationDirectRoutePlan,
        )

        self.assertIsInstance(
            result.route,
            QuantumCatRoute,
        )

        self.assertEqual(
            result.route.destination,
            "target",
        )

        self.assert_object_only(
            result
        )

    def test_hunt_route_success_has_object_target_metadata(
        self
    ):
        universe = Universe()
        universe.enable_quantum_layer()

        cat = universe.manifest_cat(
            name="object_hunter",
            source="test",
            position=
                SpatialVector3.zero(),
        )[
            "cat"
        ]

        cronenberg = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("target"),
                "test",
                "object_navigation",
            )
        )

        cronenberg.position = (
            SpatialVector3(
                x=3.0,
                y=4.0,
                z=0.0,
            )
        )

        cronenberg.size = 1.0

        result = (
            universe
            .quantum_space
            .plan_cat_route_to_nearest_huntable_cronenberg(
                cat,
                [
                    cronenberg
                ],
            )
        )

        self.assertIsInstance(
            result,
            QuantumCatRoutePlannedResult,
        )

        self.assertIs(
            result.target,
            cronenberg,
        )

        self.assertEqual(
            result.target_id,
            cronenberg.id,
        )

        self.assertAlmostEqual(
            result.target_distance,
            5.0,
        )

        self.assert_object_only(
            result
        )

    def test_hunt_route_denial_is_object(
        self
    ):
        universe = Universe()
        universe.enable_quantum_layer()

        cat = universe.manifest_cat(
            name="object_small_hunter",
            source="test",
            position=
                SpatialVector3.zero(),
        )[
            "cat"
        ]

        result = (
            universe
            .quantum_space
            .plan_cat_route_to_nearest_huntable_cronenberg(
                cat,
                [],
            )
        )

        self.assertIsInstance(
            result,
            QuantumCatRouteNotPlannedResult,
        )

        self.assertFalse(
            result.planned
        )

        self.assertEqual(
            result.reason,
            "no_huntable_cronenberg",
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
