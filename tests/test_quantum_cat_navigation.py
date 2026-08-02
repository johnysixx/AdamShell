import unittest

from universe.universe import Universe


class QuantumCatNavigationTests(
    unittest.TestCase
):

    def test_route_to_nearest_huntable_cronenberg(self):
        universe = Universe()
        universe.enable_quantum_layer()

        cat_result = universe.manifest_cat(
            name="hunter",
            source="test",
            position={
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        cat = cat_result["cat"]

        far = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("far"),
                "test",
                "hunt_navigation"
            )
        )

        far.position = {
            "x": 10.0,
            "y": 0.0,
            "z": 0.0
        }

        far.size = 1.0

        near = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("near"),
                "test",
                "hunt_navigation"
            )
        )

        near.position = {
            "x": 3.0,
            "y": 4.0,
            "z": 0.0
        }

        near.size = 1.0

        large = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("large"),
                "test",
                "hunt_navigation"
            )
        )

        large.position = {
            "x": 1.0,
            "y": 0.0,
            "z": 0.0
        }

        large.size = 2.0

        result = (
            universe
            .quantum_space
            .plan_cat_route_to_nearest_huntable_cronenberg(
                cat,
                [
                    far,
                    near,
                    large
                ],
                step_size=2.0
            )
        )

        self.assertIs(
            result["target"],
            near
        )

        self.assertEqual(
            result["target_id"],
            near.id
        )

        self.assertAlmostEqual(
            result["target_distance"],
            5.0
        )

        self.assertEqual(
            result["route"].destination,
            near.id
        )

        self.assertEqual(
            result["route"].route_steps[-1],
            near.position
        )

    def test_no_huntable_cronenberg_returns_safe_result(self):
        universe = Universe()
        universe.enable_quantum_layer()

        cat_result = universe.manifest_cat(
            name="small_hunter",
            source="test",
            position={
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        cat = cat_result["cat"]

        large = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("large"),
                "test",
                "hunt_navigation"
            )
        )

        large.position = {
            "x": 1.0,
            "y": 0.0,
            "z": 0.0
        }

        large.size = 2.0

        result = (
            universe
            .quantum_space
            .plan_cat_route_to_nearest_huntable_cronenberg(
                cat,
                [large]
            )
        )

        self.assertEqual(
            result["result"],
            "no_huntable_cronenberg"
        )

        self.assertEqual(
            result["cat_id"],
            "small_hunter"
        )

        self.assertIsNone(
            universe
            .quantum_space
            .find_cat_route(
                "small_hunter"
            )
        )

    def test_direct_cat_route_to_bar(self):
        universe = Universe()
        universe.enable_quantum_layer()

        space = universe.quantum_space

        result = space.plan_cat_route_to_bar(
            cat_id="test_cat",
            start_position={
                "x": 6.0,
                "y": 0.0,
                "z": 0.0
            },
            step_size=2.0
        )

        route = result["route"]

        self.assertEqual(
            route.destination,
            "bar_front_door"
        )

        self.assertEqual(
            route.route_steps,
            [
                {
                    "x": 4.0,
                    "y": 0.0,
                    "z": 0.0
                },
                {
                    "x": 2.0,
                    "y": 0.0,
                    "z": 0.0
                },
                {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                }
            ]
        )

        self.assertIs(
            space.find_cat_route(
                "test_cat"
            ),
            route
        )

        self.assertEqual(
            route.route_steps[-1],
            space.bar_front_door[
                "position"
            ]
        )

        self.assertEqual(
            result["plan"]["step_count"],
            3
        )

        self.assertAlmostEqual(
            result["plan"]["distance"],
            6.0
        )

    def test_direct_cat_route_to_arbitrary_target(self):
        universe = Universe()
        universe.enable_quantum_layer()

        space = universe.quantum_space

        result = space.plan_direct_cat_route(
            cat_id="hunter_cat",
            start_position={
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            destination_position={
                "x": 3.0,
                "y": 4.0,
                "z": 0.0
            },
            destination="cronenberg_target",
            step_size=2.0
        )

        route = result["route"]

        self.assertEqual(
            route.destination,
            "cronenberg_target"
        )

        self.assertEqual(
            route.route_steps[-1],
            {
                "x": 3.0,
                "y": 4.0,
                "z": 0.0
            }
        )

        self.assertAlmostEqual(
            result["plan"]["distance"],
            5.0
        )

        self.assertEqual(
            result["plan"]["step_count"],
            3
        )


if __name__ == "__main__":
    unittest.main()