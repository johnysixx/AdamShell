from types import SimpleNamespace
import unittest

from core.entity.social_entity import SocialEntity
from meeting_place.bar_arrival_protocol import BarArrivalProtocol
from meeting_place.bar_departure_protocol import BarDepartureProtocol
from meeting_place.bar_hex_geometry import BarHexGeometry
from meeting_place.bar_objects import BarPosition
from meeting_place.bar_service_protocol import BarServiceProtocol


class BarEntityPositionObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.geometry = BarHexGeometry()

    def test_bar_position_is_attribute_only_value_object(self):
        position = BarPosition(x=12.5, y=-4.0)

        self.assertEqual(position.x, 12.5)
        self.assertEqual(position.y, -4.0)
        self.assertFalse(hasattr(position, "get"))

        with self.assertRaises(TypeError):
            _ = position["x"]

    def test_arrival_creates_bar_position_object(self):
        guest = SocialEntity.from_mapping({
            "name": "guest_1",
            "type": "human",
            "state": "entering",
            "position": None,
        })

        self.assertTrue(BarArrivalProtocol(self.geometry).arrive(guest))
        self.assertIsInstance(guest.position, BarPosition)

    def test_service_rejects_mapping_position(self):
        protocol = BarServiceProtocol(self.geometry)
        target = self.geometry.find_cell(name="bar_service_floor_upper")
        bartender = SimpleNamespace(
            name="bartender",
            state="behind_bar",
            position={"x": 3000, "y": 0},
        )

        original_position = bartender.position

        self.assertFalse(protocol.move_bartender(bartender, target))
        self.assertIs(bartender.position, original_position)

    def test_departure_rejects_mapping_position(self):
        guest = SocialEntity.from_mapping({
            "name": "guest_1",
            "type": "human",
            "state": "at_bar",
            "position": {"x": 2000, "y": 0},
        })

        self.assertFalse(BarDepartureProtocol(self.geometry).leave_bar(guest))
        self.assertEqual(guest.state, "at_bar")


if __name__ == "__main__":
    unittest.main()
