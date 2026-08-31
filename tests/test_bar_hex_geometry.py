import unittest

from meeting_place.bar_hex_geometry import (
    BarHexGeometry
)


class BarHexGeometryTests(
    unittest.TestCase
):

    def setUp(self):
        self.geometry = BarHexGeometry()

    def test_hex_size_is_1000_x_1000(
        self
    ):
        self.assertEqual(
            self.geometry.hex_width,
            1000
        )

        self.assertEqual(
            self.geometry.hex_height,
            1000
        )

    def test_cells_use_xy_coordinates_only(
        self
    ):
        for cell in self.geometry.cells:
            self.assertTrue(hasattr(cell, "x"))
            self.assertTrue(hasattr(cell, "y"))
            self.assertFalse(hasattr(cell, "q"))
            self.assertFalse(hasattr(cell, "r"))
            self.assertFalse(hasattr(cell, "z"))

    def test_center_table_is_immutable_origin(
        self
    ):
        table = self.geometry.find_cell(
            name="center_table"
        )

        self.assertIsNotNone(
            table
        )

        self.assertEqual(
            table.x,
            0
        )

        self.assertEqual(
            table.y,
            0
        )

        self.assertEqual(
            table.kind,
            "table"
        )

        self.assertTrue(
            table.immutable
        )

    def test_center_has_two_immutable_chairs(
        self
    ):
        left = self.geometry.find_cell(
            name="center_chair_left"
        )

        right = self.geometry.find_cell(
            name="center_chair_right"
        )

        self.assertIsNotNone(left)
        self.assertIsNotNone(right)

        self.assertEqual(
            left.x,
            -1000
        )

        self.assertEqual(
            left.y,
            0
        )

        self.assertEqual(
            right.x,
            1000
        )

        self.assertEqual(
            right.y,
            0
        )

        self.assertTrue(
            left.seating
        )

        self.assertTrue(
            right.seating
        )

        self.assertTrue(
            left.immutable
        )

        self.assertTrue(
            right.immutable
        )

    def test_center_has_four_permanent_clearance_hexes(
        self
    ):
        clearance = self.geometry.cells_by_kind(
            "permanent_clearance"
        )

        self.assertEqual(
            len(clearance),
            4
        )

        for cell in clearance:
            self.assertTrue(
                cell.immutable
            )

            self.assertTrue(
                cell.walkable
            )

            self.assertFalse(
                cell.furniture_allowed
            )

    def test_immutable_core_contains_seven_hexes(
        self
    ):
        immutable = [
            cell
            for cell in self.geometry.cells
            if cell.immutable
        ]

        self.assertEqual(
            len(immutable),
            7
        )

    def test_floor_geometry_contains_no_window_hexes(
        self
    ):
        windows = self.geometry.cells_by_kind(
            "window"
        )

        self.assertEqual(
            windows,
            []
        )


    def test_immutable_core_ring_has_equal_radius(
        self
    ):
        center = self.geometry.find_cell(
            name="center_table"
        )

        ring = [
            cell
            for cell in self.geometry.cells
            if (
                cell.name != "center_table"
                and cell.immutable
            )
        ]

        self.assertEqual(
            len(ring),
            6
        )

        for cell in ring:
            dx = (
                cell.x
                - center.x
            )

            dy = (
                cell.y
                - center.y
            )

            distance = (
                dx ** 2
                + dy ** 2
            ) ** 0.5

            self.assertAlmostEqual(
                distance,
                1000.0,
                places=3
            )


    def test_second_ring_contains_twelve_open_floor_hexes(
        self
    ):
        ring = [
            cell
            for cell in self.geometry.cells
            if cell.ring == 2
        ]

        self.assertEqual(
            len(ring),
            12
        )

        open_floor = [
            cell
            for cell in ring
            if cell.kind == "open_floor"
        ]

        customer_floor = [
            cell
            for cell in ring
            if cell.kind == "customer_floor"
        ]

        self.assertEqual(
            len(open_floor),
            9
        )

        self.assertEqual(
            len(customer_floor),
            3
        )

        for cell in ring:
            self.assertTrue(
                cell.walkable
            )

            self.assertFalse(
                cell.immutable
            )


    def test_third_ring_contains_eighteen_bar_space_hexes(
        self
    ):
        ring = [
            cell
            for cell in self.geometry.cells
            if cell.ring == 3
        ]

        self.assertEqual(
            len(ring),
            18
        )

    def test_third_ring_contains_open_seating_and_standing_space(
        self
    ):
        ring = [
            cell
            for cell in self.geometry.cells
            if cell.ring == 3
        ]

        kinds = {
            cell.kind
            for cell in ring
        }

        self.assertIn(
            "open_floor",
            kinds
        )

        self.assertIn(
            "seating_place",
            kinds
        )

        self.assertIn(
            "standing_place",
            kinds
        )


    def test_main_bar_axis_is_entrance_center_bar_back_room(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        table = self.geometry.find_cell(
            name="center_table"
        )

        bar = self.geometry.find_cell(
            name="main_bar"
        )

        back_room = self.geometry.find_cell(
            name="back_room_door"
        )

        self.assertIsNotNone(entrance)
        self.assertIsNotNone(table)
        self.assertIsNotNone(bar)
        self.assertIsNotNone(back_room)

        self.assertEqual(
            entrance.y,
            0
        )

        self.assertEqual(
            table.y,
            0
        )

        self.assertEqual(
            bar.y,
            0
        )

        self.assertEqual(
            back_room.y,
            0
        )

        self.assertLess(
            entrance.x,
            table.x
        )

        self.assertLess(
            table.x,
            bar.x
        )

        self.assertLess(
            bar.x,
            back_room.x
        )

    def test_main_axis_features_have_correct_roles(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        bar = self.geometry.find_cell(
            name="main_bar"
        )

        back_room = self.geometry.find_cell(
            name="back_room_door"
        )

        self.assertTrue(
            entrance.door
        )

        self.assertTrue(
            entrance.walkable
        )

        self.assertEqual(
            bar.kind,
            "bar"
        )

        self.assertFalse(
            bar.walkable
        )

        self.assertTrue(
            back_room.door
        )

        self.assertEqual(
            back_room.connects_to,
            "back_room"
        )


    def test_bar_counter_is_three_hex_rear_arc(
        self
    ):
        counter = [
            cell
            for cell in self.geometry.cells
            if cell.kind == "bar"
        ]

        self.assertEqual(
            len(counter),
            3
        )

        expected_positions = {
            (3000, 0),
            (2500, -866.0254),
            (2500, 866.0254)
        }

        actual_positions = {
            (
                cell.x,
                cell.y
            )
            for cell in counter
        }

        self.assertEqual(
            actual_positions,
            expected_positions
        )

        for cell in counter:
            self.assertEqual(
                cell.ring,
                3
            )

            self.assertFalse(
                cell.walkable
            )

            self.assertFalse(
                cell.furniture_allowed
            )


    def test_bar_has_service_floor_between_counter_and_back_room(
        self
    ):
        bar = self.geometry.find_cell(
            name="main_bar"
        )

        service = self.geometry.find_cell(
            name="bar_service_floor"
        )

        back_room = self.geometry.find_cell(
            name="back_room_door"
        )

        self.assertIsNotNone(service)

        self.assertEqual(
            service.kind,
            "service_floor"
        )

        self.assertEqual(
            service.y,
            0
        )

        self.assertTrue(
            service.walkable
        )

        self.assertFalse(
            service.seating
        )

        self.assertFalse(
            service.standing
        )

        self.assertFalse(
            service.furniture_allowed
        )

        self.assertEqual(
            service.x,
            4000
        )

        self.assertEqual(
            back_room.x,
            6000
        )

        self.assertLess(
            bar.x,
            service.x
        )

        self.assertLess(
            service.x,
            back_room.x
        )


    def test_bar_has_six_hex_service_area(
        self
    ):
        service = [
            cell
            for cell in self.geometry.cells
            if cell.kind == "service_floor"
        ]

        self.assertEqual(
            len(service),
            6
        )

        expected_positions = {
            (3500, -866.0254),
            (4000, 0),
            (3500, 866.0254),
            (4500, -866.0254),
            (5000, 0),
            (4500, 866.0254)
        }

        actual_positions = {
            (
                cell.x,
                cell.y
            )
            for cell in service
        }

        self.assertEqual(
            actual_positions,
            expected_positions
        )

        for cell in service:
            self.assertTrue(
                cell.walkable
            )

            self.assertFalse(
                cell.seating
            )

            self.assertFalse(
                cell.standing
            )

            self.assertFalse(
                cell.furniture_allowed
            )


    def test_bar_has_six_hex_service_area(
        self
    ):
        service = [
            cell
            for cell in self.geometry.cells
            if cell.kind == "service_floor"
        ]

        self.assertEqual(
            len(service),
            6
        )

        expected_positions = {
            (3500, -866.0254),
            (4000, 0),
            (3500, 866.0254),
            (4500, -866.0254),
            (5000, 0),
            (4500, 866.0254)
        }

        actual_positions = {
            (
                cell.x,
                cell.y
            )
            for cell in service
        }

        self.assertEqual(
            actual_positions,
            expected_positions
        )

        for cell in service:
            self.assertTrue(
                cell.walkable
            )

            self.assertFalse(
                cell.seating
            )

            self.assertFalse(
                cell.standing
            )

            self.assertFalse(
                cell.furniture_allowed
            )


    def test_main_bar_separates_customer_and_service_space(
        self
    ):
        customer = self.geometry.find_cell(
            x=2000,
            y=0
        )

        bar = self.geometry.find_cell(
            name="main_bar"
        )

        service = self.geometry.find_cell(
            name="bar_service_floor"
        )

        self.assertIsNotNone(customer)
        self.assertIsNotNone(bar)
        self.assertIsNotNone(service)

        self.assertEqual(
            customer.kind,
            "customer_floor"
        )

        self.assertTrue(
            customer.walkable
        )

        self.assertEqual(
            bar.kind,
            "bar"
        )

        self.assertFalse(
            bar.walkable
        )

        self.assertEqual(
            service.kind,
            "service_floor"
        )

        self.assertTrue(
            service.walkable
        )

        self.assertLess(
            customer.x,
            bar.x
        )

        self.assertLess(
            bar.x,
            service.x
        )


    def test_bar_has_three_hex_customer_frontage(
        self
    ):
        customer = [
            cell
            for cell in self.geometry.cells
            if cell.kind == "customer_floor"
        ]

        self.assertEqual(
            len(customer),
            3
        )

        expected_positions = {
            (2000, 0),
            (1500, -866.0254),
            (1500, 866.0254)
        }

        actual_positions = {
            (
                cell.x,
                cell.y
            )
            for cell in customer
        }

        self.assertEqual(
            actual_positions,
            expected_positions
        )

        for cell in customer:
            self.assertEqual(
                cell.ring,
                2
            )

            self.assertTrue(
                cell.walkable
            )

            self.assertFalse(
                cell.seating
            )

            self.assertFalse(
                cell.standing
            )

            self.assertFalse(
                cell.furniture_allowed
            )


    def test_geometry_can_find_hex_neighbors(
        self
    ):
        center = self.geometry.find_cell(
            name="center_table"
        )

        neighbors = self.geometry.neighbors(
            center
        )

        self.assertEqual(
            len(neighbors),
            6
        )

        names = {
            cell.name
            for cell in neighbors
        }

        self.assertEqual(
            names,
            {
                "center_chair_left",
                "center_chair_right",
                "core_clearance_upper_left",
                "core_clearance_upper_right",
                "core_clearance_lower_left",
                "core_clearance_lower_right"
            }
        )


    def test_geometry_finds_walkable_path_from_entrance_to_bar(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        destination = self.geometry.find_cell(
            name="main_bar_customer_floor"
        )

        path = self.geometry.shortest_walkable_path(
            entrance,
            destination
        )

        self.assertIsNotNone(
            path
        )

        self.assertGreater(
            len(path),
            1
        )

        self.assertIs(
            path[0],
            entrance
        )

        self.assertIs(
            path[-1],
            destination
        )

        for cell in path:
            self.assertTrue(
                cell.walkable
            )

        names = {
            cell.name
            for cell in path
        }

        self.assertNotIn(
            "center_table",
            names
        )

        self.assertNotIn(
            "main_bar",
            names
        )


    def test_service_floor_has_walkable_path_to_back_room(
        self
    ):
        service = self.geometry.find_cell(
            name="bar_service_floor"
        )

        back_room = self.geometry.find_cell(
            name="back_room_door"
        )

        path = self.geometry.shortest_walkable_path(
            service,
            back_room
        )

        self.assertIsNotNone(
            path
        )

        self.assertIs(
            path[0],
            service
        )

        self.assertIs(
            path[-1],
            back_room
        )

        for cell in path:
            self.assertTrue(
                cell.walkable
            )


    def test_customer_space_cannot_walk_into_service_area(
        self
    ):
        customer = self.geometry.find_cell(
            name="main_bar_customer_floor"
        )

        service = self.geometry.find_cell(
            name="bar_service_floor"
        )

        path = self.geometry.shortest_walkable_path(
            customer,
            service
        )

        self.assertIsNone(
            path
        )


    def test_geometry_finds_nearest_walkable_seating_from_entrance(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        seat = self.geometry.nearest_reachable_cell(
            entrance,
            kind="seating_place"
        )

        self.assertIsNotNone(
            seat
        )

        self.assertEqual(
            seat.kind,
            "seating_place"
        )

        self.assertTrue(
            seat.walkable
        )

        path = self.geometry.shortest_walkable_path(
            entrance,
            seat
        )

        self.assertIsNotNone(
            path
        )

        self.assertIs(
            path[0],
            entrance
        )

        self.assertIs(
            path[-1],
            seat
        )


    def test_seating_and_standing_places_start_unoccupied(
        self
    ):
        places = [
            cell
            for cell in self.geometry.cells
            if cell.kind in {
                "seating_place",
                "standing_place"
            }
        ]

        self.assertGreater(
            len(places),
            0
        )

        for cell in places:
            self.assertTrue(
                hasattr(cell, "occupied_by")
            )

            self.assertIsNone(
                cell.occupied_by
            )


    def test_nearest_reachable_cell_skips_occupied_place(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        first_seat = self.geometry.nearest_reachable_cell(
            entrance,
            kind="seating_place"
        )

        self.assertIsNotNone(
            first_seat
        )

        first_seat.occupied_by = "entity_1"

        second_seat = self.geometry.nearest_reachable_cell(
            entrance,
            kind="seating_place"
        )

        self.assertIsNotNone(
            second_seat
        )

        self.assertIsNot(
            second_seat,
            first_seat
        )

        self.assertIsNone(
            second_seat.occupied_by
        )


    def test_entity_can_occupy_free_seating_place(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        seat = self.geometry.nearest_reachable_cell(
            entrance,
            kind="seating_place"
        )

        result = self.geometry.occupy_cell(
            "entity_1",
            seat
        )

        self.assertTrue(
            result
        )

        self.assertEqual(
            seat.occupied_by,
            "entity_1"
        )


    def test_entity_cannot_replace_other_occupant(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        seat = self.geometry.nearest_reachable_cell(
            entrance,
            kind="seating_place"
        )

        first = self.geometry.occupy_cell(
            "entity_1",
            seat
        )

        second = self.geometry.occupy_cell(
            "entity_2",
            seat
        )

        self.assertTrue(
            first
        )

        self.assertFalse(
            second
        )

        self.assertEqual(
            seat.occupied_by,
            "entity_1"
        )


    def test_entity_can_release_own_place(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        seat = self.geometry.nearest_reachable_cell(
            entrance,
            kind="seating_place"
        )

        self.geometry.occupy_cell(
            "entity_1",
            seat
        )

        result = self.geometry.release_cell(
            "entity_1",
            seat
        )

        self.assertTrue(
            result
        )

        self.assertIsNone(
            seat.occupied_by
        )


    def test_entity_cannot_release_other_occupants_place(
        self
    ):
        entrance = self.geometry.find_cell(
            name="entrance_door"
        )

        seat = self.geometry.nearest_reachable_cell(
            entrance,
            kind="seating_place"
        )

        self.geometry.occupy_cell(
            "entity_1",
            seat
        )

        result = self.geometry.release_cell(
            "entity_2",
            seat
        )

        self.assertFalse(
            result
        )

        self.assertEqual(
            seat.occupied_by,
            "entity_1"
        )


    def test_initial_bar_has_three_modules_and_two_deep_service_area(
        self
    ):
        customer = [
            cell
            for cell in self.geometry.cells
            if cell.kind == "customer_floor"
        ]

        bar = [
            cell
            for cell in self.geometry.cells
            if cell.kind == "bar"
        ]

        service = [
            cell
            for cell in self.geometry.cells
            if cell.kind == "service_floor"
        ]

        self.assertEqual(
            len(customer),
            3
        )

        self.assertEqual(
            len(bar),
            3
        )

        self.assertEqual(
            len(service),
            6
        )

        expected_service_positions = {
            (3500, -866.0254),
            (4000, 0),
            (3500, 866.0254),
            (4500, -866.0254),
            (5000, 0),
            (4500, 866.0254)
        }

        actual_service_positions = {
            (
                cell.x,
                cell.y
            )
            for cell in service
        }

        self.assertEqual(
            actual_service_positions,
            expected_service_positions
        )

        back_room = self.geometry.find_cell(
            name="back_room_door"
        )

        self.assertEqual(
            back_room.x,
            6000
        )

        self.assertEqual(
            back_room.y,
            0
        )


if __name__ == "__main__":
    unittest.main()




