class SpatialComponent:

    AXES = (
        "x",
        "y",
        "z"
    )

    def __init__(
        self,
        position=None,
        layer=None,
        zone=None
    ):
        self.name = "spatial_component"
        self.type = "entity_component"

        self._position = None
        self.layer = layer
        self.zone = zone

        self.velocity = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        self.rotation = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        if position is not None:
            self.set_position(
                position
            )

    @property
    def position(self):
        if self._position is None:
            return None

        return dict(
            self._position
        )

    @property
    def has_position(self):
        return self._position is not None

    def set_position(
        self,
        position
    ):
        self._position = (
            self._normalize_vector(
                position,
                field_name="position"
            )
        )

        return self.position

    def clear_position(self):
        previous_position = self.position
        self._position = None

        return previous_position

    def move_to(
        self,
        position,
        layer=None,
        zone=None
    ):
        previous_position = self.position

        current_position = self.set_position(
            position
        )

        if layer is not None:
            self.layer = layer

        if zone is not None:
            self.zone = zone

        return {
            "name": "spatial_position_changed",
            "previous_position": (
                previous_position
            ),
            "current_position": (
                current_position
            ),
            "layer": self.layer,
            "zone": self.zone
        }

    def set_velocity(
        self,
        velocity
    ):
        self.velocity = (
            self._normalize_vector(
                velocity,
                field_name="velocity"
            )
        )

        return dict(
            self.velocity
        )

    def set_rotation(
        self,
        rotation
    ):
        self.rotation = (
            self._normalize_vector(
                rotation,
                field_name="rotation"
            )
        )

        return dict(
            self.rotation
        )

    def _normalize_vector(
        self,
        value,
        field_name
    ):
        if not isinstance(
            value,
            dict
        ):
            raise TypeError(
                f"Spatial {field_name} "
                "must be a dictionary."
            )

        missing_axes = [
            axis
            for axis in self.AXES
            if axis not in value
        ]

        if missing_axes:
            raise ValueError(
                f"Spatial {field_name} "
                "is missing axes: "
                + ", ".join(
                    missing_axes
                )
            )

        return {
            axis: float(
                value[axis]
            )
            for axis in self.AXES
        }

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "position": self.position,
            "has_position": (
                self.has_position
            ),
            "layer": self.layer,
            "zone": self.zone,
            "velocity": dict(
                self.velocity
            ),
            "rotation": dict(
                self.rotation
            )
        }
