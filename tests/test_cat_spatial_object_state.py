import unittest

from cats.cat_knowledge_objects import CatKnownPlace
from cats.cat_perception_state import CatScentTransferCandidate
from cats.cats import Cats
from core.entity.components import SpatialVector3
from meeting_place.bar_objects import BarPosition
from navigation import NavigationEngine
from universe.universe import Universe


class CatSpatialObjectStateTests(unittest.TestCase):

    def test_cat_position_requires_spatial_vector(self):
        universe = Universe()
        cat = Cats(universe).create_cat(
            name="spatial_cat",
            color="black",
            fur_length="short",
        )
        with self.assertRaises(TypeError):
            cat.position = {"x": 1.0, "y": 2.0, "z": 3.0}
        position = SpatialVector3(x=1.0, y=2.0, z=3.0)
        event = cat.move_to(position)
        self.assertIs(cat.position, position)
        self.assertEqual(event["position"], position.to_dict())
        self.assertIsInstance(event["position"], dict)

    def test_bar_position_uses_same_spatial_contract(self):
        universe = Universe()
        cat = Cats(universe).create_cat(
            name="bar_cat",
            color="black",
            fur_length="short",
        )
        position = BarPosition(x=4.0, y=5.0)
        cat.move_to(position)
        self.assertIsInstance(position, SpatialVector3)
        self.assertIs(cat.position, position)
        self.assertEqual(position.z, 0.0)

    def test_navigation_rejects_mapping_positions(self):
        engine = NavigationEngine()
        with self.assertRaises(TypeError):
            engine.direct_route(
                {"x": 0.0, "y": 0.0, "z": 0.0},
                SpatialVector3.zero(),
            )

    def test_cat_spatial_substate_rejects_mapping_positions(self):
        with self.assertRaises(TypeError):
            CatKnownPlace(
                layer="quantum_layer",
                position={"x": 1.0, "y": 2.0, "z": 3.0},
            )
        with self.assertRaises(TypeError):
            CatScentTransferCandidate(
                box_position={"x": 1.0, "y": 2.0, "z": 3.0},
            )

    def test_quantum_route_moves_cat_with_spatial_object(self):
        universe = Universe()
        universe.enable_quantum_layer()
        cats = Cats(universe)
        cat = cats.create_cat(
            name="route_cat",
            color="black",
            fur_length="short",
        )
        cat.current_layer = "quantum_layer"
        start = SpatialVector3.zero()
        destination = SpatialVector3(x=1.0, y=0.0, z=0.0)
        cat.move_to(start)
        universe.quantum_space.plan_direct_cat_route(
            cat_id=cat.name,
            start_position=start,
            destination_position=destination,
            destination="test_destination",
            step_size=1.0,
        )
        result = universe.quantum_space.advance_cat_route(
            cat=cat,
            cronenbergs=[],
            encounter_system=universe.cat_cronenberg_encounter,
            universe=universe,
        )
        self.assertIsInstance(cat.position, SpatialVector3)
        self.assertEqual(cat.position, destination)
        self.assertIsInstance(result["position"], dict)
        self.assertEqual(result["position"], destination.to_dict())

    def test_spatial_vector_domain_operations_are_object_only(self):
        origin = SpatialVector3.zero()
        destination = origin.translated(dx=2.0, dy=-1.0, dz=3.0)
        self.assertEqual(
            destination,
            SpatialVector3(x=2.0, y=-1.0, z=3.0),
        )
        self.assertEqual(origin.manhattan_distance_to(destination), 6.0)
        self.assertTrue(
            destination.is_close_to(
                SpatialVector3(x=2.0, y=-1.0, z=3.0)
            )
        )
        with self.assertRaises(TypeError):
            destination.distance_to(
                {"x": 0.0, "y": 0.0, "z": 0.0}
            )


if __name__ == "__main__":
    unittest.main()
