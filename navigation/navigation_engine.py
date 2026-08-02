import math


class NavigationEngine:

    AXES = (
        "x",
        "y",
        "z"
    )

    def __init__(
        self,
        default_step_size=1.0
    ):
        default_step_size = float(
            default_step_size
        )

        if default_step_size <= 0.0:
            raise ValueError(
                "Navigation step size must be positive."
            )

        self.name = "navigation_engine"
        self.type = "route_planner"

        self.default_step_size = (
            default_step_size
        )

        self.route_count = 0

    def direct_route(
        self,
        start_position,
        destination_position,
        step_size=None
    ):
        start = self._normalize_position(
            start_position
        )

        destination = self._normalize_position(
            destination_position
        )

        step_size = (
            self.default_step_size
            if step_size is None
            else float(step_size)
        )

        if step_size <= 0.0:
            raise ValueError(
                "Navigation step size must be positive."
            )

        distance = self.distance(
            start,
            destination
        )

        if distance == 0.0:
            route_steps = []
        else:
            step_count = max(
                1,
                math.ceil(
                    distance / step_size
                )
            )

            route_steps = [
                {
                    axis: (
                        start[axis]
                        + (
                            destination[axis]
                            - start[axis]
                        )
                        * index
                        / step_count
                    )
                    for axis in self.AXES
                }
                for index in range(
                    1,
                    step_count + 1
                )
            ]

        self.route_count += 1

        return {
            "name": "direct_route_planned",
            "route_number": self.route_count,
            "start_position": start,
            "destination_position": (
                destination
            ),
            "distance": distance,
            "step_size": step_size,
            "step_count": len(
                route_steps
            ),
            "route_steps": route_steps
        }

    def nearest_target(
        self,
        origin_position,
        candidates,
        position_getter=None
    ):
        origin = self._normalize_position(
            origin_position
        )

        if position_getter is None:
            position_getter = (
                lambda candidate: getattr(
                    candidate,
                    "position",
                    None
                )
            )

        available = []

        for candidate in candidates:
            position = position_getter(
                candidate
            )

            if position is None:
                continue

            normalized_position = (
                self._normalize_position(
                    position
                )
            )

            available.append({
                "target": candidate,
                "position": (
                    normalized_position
                ),
                "distance": self.distance(
                    origin,
                    normalized_position
                )
            })

        if not available:
            return None

        return min(
            available,
            key=lambda item: item[
                "distance"
            ]
        )

    def distance(
        self,
        first_position,
        second_position
    ):
        first = self._normalize_position(
            first_position
        )

        second = self._normalize_position(
            second_position
        )

        return math.sqrt(
            sum(
                (
                    second[axis]
                    - first[axis]
                ) ** 2
                for axis in self.AXES
            )
        )

    def _normalize_position(
        self,
        position
    ):
        if not isinstance(
            position,
            dict
        ):
            raise TypeError(
                "Navigation position must be a dictionary."
            )

        missing_axes = [
            axis
            for axis in self.AXES
            if axis not in position
        ]

        if missing_axes:
            raise ValueError(
                "Navigation position is missing axes: "
                + ", ".join(missing_axes)
            )

        return {
            axis: float(
                position[axis]
            )
            for axis in self.AXES
        }

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "default_step_size": (
                self.default_step_size
            ),
            "route_count": (
                self.route_count
            )
        }
