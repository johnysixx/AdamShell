import unittest

from meeting_place.bar_hex_geometry import (
    BarHexGeometry
)

from meeting_place.bar_service_protocol import (
    BarServiceProtocol
)


class BarServiceProtocolTests(
    unittest.TestCase
):

    def setUp(self):
        self.geometry = BarHexGeometry()

        self.protocol = BarServiceProtocol(
            self.geometry
        )

    def test_bartender_starts_behind_center_of_bar(
        self
    ):
        bartender = {
            "name": "bartender",
            "state": "created",
            "position": None
        }

        result = self.protocol.place_bartender(
            bartender
        )

        self.assertTrue(
            result
        )

        self.assertEqual(
            bartender["state"],
            "behind_bar"
        )

        self.assertIsNotNone(
            bartender["position"]
        )

        cell = self.geometry.find_cell(
            x=bartender["position"]["x"],
            y=bartender["position"]["y"]
        )

        self.assertIsNotNone(
            cell
        )

        self.assertEqual(
            cell["name"],
            "bar_service_floor"
        )

        self.assertEqual(
            cell["kind"],
            "service_floor"
        )


    def test_bartender_can_move_only_within_service_area(
        self
    ):
        bartender = {
            "name": "bartender",
            "state": "created",
            "position": None
        }

        self.assertTrue(
            self.protocol.place_bartender(
                bartender
            )
        )

        target_service = self.geometry.find_cell(
            name="bar_service_floor_upper"
        )

        self.assertIsNotNone(
            target_service
        )

        moved = self.protocol.move_bartender(
            bartender,
            target_service
        )

        self.assertTrue(
            moved
        )

        self.assertEqual(
            bartender["position"],
            {
                "x": target_service["x"],
                "y": target_service["y"]
            }
        )

        customer = self.geometry.find_cell(
            name="main_bar_customer_floor"
        )

        self.assertIsNotNone(
            customer
        )

        position_before = dict(
            bartender["position"]
        )

        rejected = self.protocol.move_bartender(
            bartender,
            customer
        )

        self.assertFalse(
            rejected
        )

        self.assertEqual(
            bartender["position"],
            position_before
        )


if __name__ == "__main__":
    unittest.main()

