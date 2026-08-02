import unittest

from navigation import NavigationEngine


class NavigationEngineTests(
    unittest.TestCase
):

    def test_direct_route_reaches_destination(self):
        engine = NavigationEngine(
            default_step_size=2.0
        )

        result = engine.direct_route(
            {
                "x": 6.0,
                "y": 0.0,
                "z": 0.0
            },
            {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.assertAlmostEqual(
            result["distance"],
            6.0
        )

        self.assertEqual(
            result["step_count"],
            3
        )

        self.assertEqual(
            result["route_steps"][-1],
            {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.assertEqual(
            result["route_steps"],
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

    def test_zero_distance_creates_empty_route(self):
        engine = NavigationEngine()

        result = engine.direct_route(
            {
                "x": 1.0,
                "y": 2.0,
                "z": 3.0
            },
            {
                "x": 1.0,
                "y": 2.0,
                "z": 3.0
            }
        )

        self.assertEqual(
            result["distance"],
            0.0
        )

        self.assertEqual(
            result["step_count"],
            0
        )

        self.assertEqual(
            result["route_steps"],
            []
        )

    def test_invalid_step_size_is_rejected(self):
        with self.assertRaises(
            ValueError
        ):
            NavigationEngine(
                default_step_size=0
            )


if __name__ == "__main__":
    unittest.main()