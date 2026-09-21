import unittest

from core.entity.components import SpatialVector3
from core.entity.quantum_cat_route import (
    QuantumCatRoute,
    QuantumCatRouteDetour,
)


class QuantumCatRouteObjectStateTests(unittest.TestCase):

    def create_route(self):
        return QuantumCatRoute(
            cat_id="route_cat",
            route_steps=[
                SpatialVector3(x=1.0, y=0.0, z=0.0),
                SpatialVector3(x=2.0, y=0.0, z=0.0),
            ],
            start_position=SpatialVector3.zero(),
            destination="target",
        )

    def test_route_positions_are_spatial_vectors(self):
        route = self.create_route()

        self.assertIsInstance(route.start_position, SpatialVector3)
        self.assertIsInstance(route.current_position, SpatialVector3)
        self.assertTrue(
            all(
                isinstance(step, SpatialVector3)
                for step in route.route_steps
            )
        )
        self.assertIsInstance(route.next_position, SpatialVector3)

    def test_route_rejects_mapping_positions(self):
        with self.assertRaises(TypeError):
            QuantumCatRoute(
                cat_id="legacy_route",
                route_steps=[
                    {"x": 1.0, "y": 0.0, "z": 0.0}
                ],
                start_position=SpatialVector3.zero(),
            )

        with self.assertRaises(TypeError):
            QuantumCatRoute(
                cat_id="legacy_start",
                route_steps=[
                    SpatialVector3(x=1.0, y=0.0, z=0.0)
                ],
                start_position={"x": 0.0, "y": 0.0, "z": 0.0},
            )

    def test_detour_is_object_state(self):
        route = self.create_route()
        blocked = SpatialVector3(x=1.0, y=0.0, z=0.0)

        detour_position = route.make_minimal_detour(blocked)

        self.assertIsInstance(detour_position, SpatialVector3)
        self.assertEqual(len(route.detours), 1)
        self.assertIsInstance(route.detours[0], QuantumCatRouteDetour)
        self.assertEqual(route.detours[0].blocked_position, blocked)
        self.assertEqual(route.detours[0].detour_position, detour_position)
        self.assertEqual(route.detour_count_for(blocked), 1)

    def test_detour_rejects_mapping_position(self):
        route = self.create_route()

        with self.assertRaises(TypeError):
            route.make_minimal_detour(
                {"x": 1.0, "y": 0.0, "z": 0.0}
            )

    def test_public_state_is_detached_serialization(self):
        route = self.create_route()
        route.make_minimal_detour(
            SpatialVector3(x=1.0, y=0.0, z=0.0)
        )

        snapshot = route.public_state
        snapshot["route_steps"][0]["x"] = 99.0
        snapshot["detours"][0]["detour_position"]["y"] = 99.0

        self.assertEqual(route.route_steps[0].x, 1.0)
        self.assertEqual(route.detours[0].detour_position.y, 0.25)


if __name__ == "__main__":
    unittest.main()
