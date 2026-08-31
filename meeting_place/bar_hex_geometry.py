from meeting_place.bar_objects import BarHexCell

class BarHexGeometry:

    HEX_WIDTH = 1000
    HEX_HEIGHT = 1000

    def __init__(self):
        self.name = "bar_hex_geometry"
        self.type = "bar_geometry"

        self.hex_width = self.HEX_WIDTH
        self.hex_height = self.HEX_HEIGHT

        self.cells = []

        self.build_immutable_core()
        self.build_second_ring()
        self.build_third_ring()
        self.build_main_axis()

    def _cell(
        self,
        name,
        x,
        y,
        kind,
        walkable=True,
        standing=False,
        seating=False,
        door=False,
        connects_to=None,
        immutable=False,
        furniture_allowed=True,
        ring=None,
        occupied_by=None
    ):
        return BarHexCell(
            name=name,
            x=x,
            y=y,
            kind=kind,
            walkable=walkable,
            standing=standing,
            seating=seating,
            door=door,
            connects_to=connects_to,
            immutable=immutable,
            furniture_allowed=furniture_allowed,
            ring=ring,
            occupied_by=occupied_by,
        )

    def build_immutable_core(self):
        self.cells = [
            self._cell(
                name="center_table",
                x=0,
                y=0,
                kind="table",
                walkable=False,
                immutable=True,
                furniture_allowed=False,
                ring=0
            ),

            self._cell(
                name="center_chair_left",
                x=-1000,
                y=0,
                kind="chair",
                walkable=False,
                seating=True,
                immutable=True,
                furniture_allowed=False,
                ring=1
            ),

            self._cell(
                name="center_chair_right",
                x=1000,
                y=0,
                kind="chair",
                walkable=False,
                seating=True,
                immutable=True,
                furniture_allowed=False,
                ring=1
            ),

            self._cell(
                name="core_clearance_upper_left",
                x=-500,
                y=-866.0254,
                kind="permanent_clearance",
                walkable=True,
                immutable=True,
                furniture_allowed=False,
                ring=1
            ),

            self._cell(
                name="core_clearance_upper_right",
                x=500,
                y=-866.0254,
                kind="permanent_clearance",
                walkable=True,
                immutable=True,
                furniture_allowed=False,
                ring=1
            ),

            self._cell(
                name="core_clearance_lower_left",
                x=-500,
                y=866.0254,
                kind="permanent_clearance",
                walkable=True,
                immutable=True,
                furniture_allowed=False,
                ring=1
            ),

            self._cell(
                name="core_clearance_lower_right",
                x=500,
                y=866.0254,
                kind="permanent_clearance",
                walkable=True,
                immutable=True,
                furniture_allowed=False,
                ring=1
            )
        ]

    def build_second_ring(self):
        positions = [
            (2000, 0),
            (1500, 866.0254),
            (1000, 1732.0508),
            (0, 1732.0508),
            (-1000, 1732.0508),
            (-1500, 866.0254),
            (-2000, 0),
            (-1500, -866.0254),
            (-1000, -1732.0508),
            (0, -1732.0508),
            (1000, -1732.0508),
            (1500, -866.0254)
        ]

        for index, position in enumerate(
            positions,
            start=1
        ):
            x, y = position

            self.cells.append(
                self._cell(
                    name=(
                        f"open_floor_ring_2_"
                        f"{index:02d}"
                    ),
                    x=x,
                    y=y,
                    kind="open_floor",
                    walkable=True,
                    immutable=False,
                    furniture_allowed=True,
                    ring=2
                )
            )

    def build_third_ring(self):
        layout = [
            (3000, 0, "standing_place"),
            (2500, 866.0254, "seating_place"),
            (2000, 1732.0508, "seating_place"),

            (1500, 2598.0762, "open_floor"),
            (500, 2598.0762, "open_floor"),
            (-500, 2598.0762, "open_floor"),
            (-1500, 2598.0762, "open_floor"),

            (-2000, 1732.0508, "seating_place"),
            (-2500, 866.0254, "seating_place"),
            (-3000, 0, "standing_place"),

            (-2500, -866.0254, "standing_place"),
            (-2000, -1732.0508, "seating_place"),

            (-1500, -2598.0762, "open_floor"),
            (-500, -2598.0762, "open_floor"),
            (500, -2598.0762, "open_floor"),
            (1500, -2598.0762, "open_floor"),

            (2000, -1732.0508, "seating_place"),
            (2500, -866.0254, "standing_place")
        ]

        for index, item in enumerate(
            layout,
            start=1
        ):
            x, y, kind = item

            self.cells.append(
                self._cell(
                    name=(
                        f"bar_ring_3_"
                        f"{index:02d}"
                    ),
                    x=x,
                    y=y,
                    kind=kind,
                    walkable=True,
                    standing=(
                        kind
                        == "standing_place"
                    ),
                    seating=(
                        kind
                        == "seating_place"
                    ),
                    immutable=False,
                    furniture_allowed=True,
                    ring=3
                )
            )

    def build_main_axis(self):
        customer_floor = self.find_cell(
            x=2000,
            y=0
        )

        if customer_floor is None:
            raise ValueError(
                "Customer floor axis hex is missing."
            )

        customer_floor.name = 'main_bar_customer_floor'
        customer_floor.kind = 'customer_floor'
        customer_floor.walkable = True
        customer_floor.standing = False
        customer_floor.seating = False
        customer_floor.door = False
        customer_floor.connects_to = None
        customer_floor.furniture_allowed = False

        customer_upper = self.find_cell(
            x=1500,
            y=-866.0254
        )

        if customer_upper is None:
            raise ValueError(
                "Upper customer frontage hex is missing."
            )

        customer_upper.name = 'main_bar_customer_upper'
        customer_upper.kind = 'customer_floor'
        customer_upper.walkable = True
        customer_upper.standing = False
        customer_upper.seating = False
        customer_upper.door = False
        customer_upper.connects_to = None
        customer_upper.furniture_allowed = False

        customer_lower = self.find_cell(
            x=1500,
            y=866.0254
        )

        if customer_lower is None:
            raise ValueError(
                "Lower customer frontage hex is missing."
            )

        customer_lower.name = 'main_bar_customer_lower'
        customer_lower.kind = 'customer_floor'
        customer_lower.walkable = True
        customer_lower.standing = False
        customer_lower.seating = False
        customer_lower.door = False
        customer_lower.connects_to = None
        customer_lower.furniture_allowed = False

        entrance = self.find_cell(
            x=-3000,
            y=0
        )

        if entrance is None:
            raise ValueError(
                "Entrance axis hex is missing."
            )

        entrance.name = 'entrance_door'
        entrance.kind = 'entrance'
        entrance.walkable = True
        entrance.standing = False
        entrance.seating = False
        entrance.door = True
        entrance.connects_to = 'outside_front_door'
        entrance.furniture_allowed = False

        bar = self.find_cell(
            x=3000,
            y=0
        )

        if bar is None:
            raise ValueError(
                "Main bar axis hex is missing."
            )

        bar.name = 'main_bar'
        bar.kind = 'bar'
        bar.walkable = False
        bar.standing = False
        bar.seating = False
        bar.door = False
        bar.connects_to = None
        bar.furniture_allowed = False

        bar_upper = self.find_cell(
            x=2500,
            y=-866.0254
        )

        if bar_upper is None:
            raise ValueError(
                "Upper bar counter hex is missing."
            )

        bar_upper.name = 'main_bar_upper'
        bar_upper.kind = 'bar'
        bar_upper.walkable = False
        bar_upper.standing = False
        bar_upper.seating = False
        bar_upper.door = False
        bar_upper.connects_to = None
        bar_upper.furniture_allowed = False

        bar_lower = self.find_cell(
            x=2500,
            y=866.0254
        )

        if bar_lower is None:
            raise ValueError(
                "Lower bar counter hex is missing."
            )

        bar_lower.name = 'main_bar_lower'
        bar_lower.kind = 'bar'
        bar_lower.walkable = False
        bar_lower.standing = False
        bar_lower.seating = False
        bar_lower.door = False
        bar_lower.connects_to = None
        bar_lower.furniture_allowed = False

        self.cells.append(
            self._cell(
                name="bar_service_floor",
                x=4000,
                y=0,
                kind="service_floor",
                walkable=True,
                standing=False,
                seating=False,
                door=False,
                connects_to=None,
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

        self.cells.append(
            self._cell(
                name="bar_service_floor_upper",
                x=3500,
                y=-866.0254,
                kind="service_floor",
                walkable=True,
                standing=False,
                seating=False,
                door=False,
                connects_to=None,
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

        self.cells.append(
            self._cell(
                name="bar_service_floor_lower",
                x=3500,
                y=866.0254,
                kind="service_floor",
                walkable=True,
                standing=False,
                seating=False,
                door=False,
                connects_to=None,
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

        self.cells.append(
            self._cell(
                name="bar_service_floor_deep_upper",
                x=4500,
                y=-866.0254,
                kind="service_floor",
                walkable=True,
                standing=False,
                seating=False,
                door=False,
                connects_to=None,
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

        self.cells.append(
            self._cell(
                name="bar_service_floor_deep_center",
                x=5000,
                y=0,
                kind="service_floor",
                walkable=True,
                standing=False,
                seating=False,
                door=False,
                connects_to=None,
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

        self.cells.append(
            self._cell(
                name="bar_service_floor_deep_lower",
                x=4500,
                y=866.0254,
                kind="service_floor",
                walkable=True,
                standing=False,
                seating=False,
                door=False,
                connects_to=None,
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

        self.cells.append(
            self._cell(
                name="back_room_door",
                x=6000,
                y=0,
                kind="back_room_door",
                walkable=True,
                standing=False,
                seating=False,
                door=True,
                connects_to="back_room",
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

    def neighbors(
        self,
        cell,
        tolerance=0.01
    ):
        neighbors = []

        for candidate in self.cells:
            if candidate is cell:
                continue

            dx = (
                candidate.x
                - cell.x
            )

            dy = (
                candidate.y
                - cell.y
            )

            distance = (
                dx ** 2
                + dy ** 2
            ) ** 0.5

            if abs(
                distance
                - self.HEX_WIDTH
            ) <= tolerance:
                neighbors.append(
                    candidate
                )

        return neighbors

    def neighbors(
        self,
        cell,
        tolerance=0.01
    ):
        neighbors = []

        for candidate in self.cells:
            if candidate is cell:
                continue

            dx = (
                candidate.x
                - cell.x
            )

            dy = (
                candidate.y
                - cell.y
            )

            distance = (
                dx ** 2
                + dy ** 2
            ) ** 0.5

            if abs(
                distance
                - self.HEX_WIDTH
            ) <= tolerance:
                neighbors.append(
                    candidate
                )

        return neighbors

    def shortest_walkable_path(
        self,
        start,
        destination
    ):
        if (
            start is None
            or destination is None
        ):
            return None

        if (
            not start.walkable
            or not destination.walkable
        ):
            return None

        if start is destination:
            return [start]

        queue = [
            (
                start,
                [start]
            )
        ]

        visited = {
            start.name
        }

        cursor = 0

        while cursor < len(queue):
            current, path = queue[
                cursor
            ]

            cursor += 1

            for neighbor in self.neighbors(
                current
            ):
                if not neighbor.walkable:
                    continue

                if (
                    neighbor.name
                    in visited
                ):
                    continue

                new_path = (
                    path
                    + [neighbor]
                )

                if neighbor is destination:
                    return new_path

                visited.add(
                    neighbor.name
                )

                queue.append(
                    (
                        neighbor,
                        new_path
                    )
                )

        return None

    def expand_bar(
        self
    ):
        bar_cells = [
            cell
            for cell in self.cells
            if cell.kind == "bar"
        ]

        bar_count = len(
            bar_cells
        )

        if bar_count < 3:
            return None

        extra_index = (
            bar_count
            - 3
        )

        level = (
            2
            + extra_index // 2
        )

        side = (
            -1
            if extra_index % 2 == 0
            else 1
        )

        y = round(
            side
            * 866.0254
            * level,
            4
        )

        customer_x = (
            2000
            - 500 * level
        )

        bar_x = (
            customer_x
            + 1000
        )

        service_front_x = (
            customer_x
            + 2000
        )

        service_back_x = (
            customer_x
            + 3000
        )

        customer = self.find_cell(
            x=customer_x,
            y=y
        )

        bar = self.find_cell(
            x=bar_x,
            y=y
        )

        if (
            customer is None
            or bar is None
        ):
            return None

        if (
            customer.occupied_by
            is not None
            or bar.occupied_by
            is not None
        ):
            return None

        service_front_existing = (
            self.find_cell(
                x=service_front_x,
                y=y
            )
        )

        service_back_existing = (
            self.find_cell(
                x=service_back_x,
                y=y
            )
        )

        if (
            service_front_existing
            is not None
            or service_back_existing
            is not None
        ):
            return None

        module_number = (
            bar_count
            + 1
        )

        customer.name = (
            "dynamic_customer_floor_"
            f"{module_number:02d}"
        )
        customer.kind = "customer_floor"
        customer.walkable = True
        customer.standing = False
        customer.seating = False
        customer.door = False
        customer.connects_to = None
        customer.furniture_allowed = False

        bar.name = (
            "dynamic_bar_"
            f"{module_number:02d}"
        )
        bar.kind = "bar"
        bar.walkable = False
        bar.standing = False
        bar.seating = False
        bar.door = False
        bar.connects_to = None
        bar.furniture_allowed = False

        self.cells.append(
            self._cell(
                name=(
                    "dynamic_service_front_"
                    f"{module_number:02d}"
                ),
                x=service_front_x,
                y=y,
                kind="service_floor",
                walkable=True,
                standing=False,
                seating=False,
                door=False,
                connects_to=None,
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

        self.cells.append(
            self._cell(
                name=(
                    "dynamic_service_back_"
                    f"{module_number:02d}"
                ),
                x=service_back_x,
                y=y,
                kind="service_floor",
                walkable=True,
                standing=False,
                seating=False,
                door=False,
                connects_to=None,
                immutable=False,
                furniture_allowed=False,
                ring=None
            )
        )

        return customer
    def occupy_cell(
        self,
        entity_id,
        cell
    ):
        if (
            entity_id is None
            or cell is None
        ):
            return False

        belongs_to_geometry = any(
            candidate is cell
            for candidate in self.cells
        )

        if not belongs_to_geometry:
            return False

        if cell.kind not in {
            "seating_place",
            "standing_place",
            "customer_floor"
        }:
            return False

        if cell.occupied_by is not None:
            return False

        cell.occupied_by = entity_id

        return True

    def release_cell(
        self,
        entity_id,
        cell
    ):
        if (
            entity_id is None
            or cell is None
        ):
            return False

        belongs_to_geometry = any(
            candidate is cell
            for candidate in self.cells
        )

        if not belongs_to_geometry:
            return False

        if cell.occupied_by != entity_id:
            return False

        cell.occupied_by = None

        return True

    def nearest_reachable_cell(
        self,
        start,
        kind=None
    ):
        if start is None:
            return None

        if not start.walkable:
            return None

        queue = [start]

        visited = {
            start.name
        }

        cursor = 0

        while cursor < len(queue):
            current = queue[
                cursor
            ]

            cursor += 1

            matches_kind = (
                kind is None
                or current.kind == kind
            )

            is_available = (
                current.occupied_by
                is None
            )

            if (
                matches_kind
                and is_available
            ):
                return current

            for neighbor in self.neighbors(
                current
            ):
                if not neighbor.walkable:
                    continue

                if (
                    neighbor.name
                    in visited
                ):
                    continue

                visited.add(
                    neighbor.name
                )

                queue.append(
                    neighbor
                )

        return None

    def find_cell(
        self,
        name=None,
        kind=None,
        x=None,
        y=None
    ):
        for cell in self.cells:
            if (
                name is not None
                and cell.name != name
            ):
                continue

            if (
                kind is not None
                and cell.kind != kind
            ):
                continue

            if (
                x is not None
                and cell.x != x
            ):
                continue

            if (
                y is not None
                and cell.y != y
            ):
                continue

            return cell

        return None

    def cells_by_kind(
        self,
        kind
    ):
        return [
            cell
            for cell in self.cells
            if cell.kind == kind
        ]

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "hex_width": self.hex_width,
            "hex_height": self.hex_height,
            "cell_count": len(
                self.cells
            ),
            "cells": [
                cell.to_dict()
                for cell in self.cells
            ]
        }




