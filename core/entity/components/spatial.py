from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SpatialVector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __post_init__(self):
        object.__setattr__(self, "x", float(self.x))
        object.__setattr__(self, "y", float(self.y))
        object.__setattr__(self, "z", float(self.z))

    @classmethod
    def zero(cls):
        return cls()

    def distance_to(self, other):
        other = require_spatial_vector(
            other,
            field_name="distance target",
        )
        return (
            (other.x - self.x) ** 2
            + (other.y - self.y) ** 2
            + (other.z - self.z) ** 2
        ) ** 0.5

    def manhattan_distance_to(self, other):
        other = require_spatial_vector(
            other,
            field_name="Manhattan-distance target",
        )
        return (
            abs(other.x - self.x)
            + abs(other.y - self.y)
            + abs(other.z - self.z)
        )

    def is_close_to(self, other, tolerance=1e-09):
        other = require_spatial_vector(
            other,
            field_name="comparison position",
        )
        tolerance = float(tolerance)
        if tolerance < 0.0:
            raise ValueError(
                "Spatial comparison tolerance must not be negative."
            )
        return (
            abs(other.x - self.x) <= tolerance
            and abs(other.y - self.y) <= tolerance
            and abs(other.z - self.z) <= tolerance
        )

    def translated(self, *, dx=0.0, dy=0.0, dz=0.0):
        return SpatialVector3(
            x=self.x + float(dx),
            y=self.y + float(dy),
            z=self.z + float(dz),
        )

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }


def require_spatial_vector(value, field_name="position"):
    if not isinstance(value, SpatialVector3):
        raise TypeError(
            f"Spatial {field_name} must be a SpatialVector3 object."
        )
    return value


def require_optional_spatial_vector(value, field_name="position"):
    if value is None:
        return None
    return require_spatial_vector(
        value,
        field_name=field_name,
    )


class SpatialComponent:

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

        self.velocity = SpatialVector3.zero()
        self.rotation = SpatialVector3.zero()

        if position is not None:
            self.set_position(position)

    @property
    def position(self):
        return self._position

    @property
    def has_position(self):
        return self._position is not None

    @staticmethod
    def _require_vector(value, field_name):
        return require_spatial_vector(
            value,
            field_name=field_name,
        )

    def set_position(self, position):
        self._position = self._require_vector(
            position,
            field_name="position",
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
        current_position = self.set_position(position)

        if layer is not None:
            self.layer = layer

        if zone is not None:
            self.zone = zone

        return {
            "name": "spatial_position_changed",
            "previous_position": (
                None
                if previous_position is None
                else previous_position.to_dict()
            ),
            "current_position": current_position.to_dict(),
            "layer": self.layer,
            "zone": self.zone,
        }

    def set_velocity(self, velocity):
        self.velocity = self._require_vector(
            velocity,
            field_name="velocity",
        )
        return self.velocity

    def set_rotation(self, rotation):
        self.rotation = self._require_vector(
            rotation,
            field_name="rotation",
        )
        return self.rotation

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "position": (
                None
                if self.position is None
                else self.position.to_dict()
            ),
            "has_position": self.has_position,
            "layer": self.layer,
            "zone": self.zone,
            "velocity": self.velocity.to_dict(),
            "rotation": self.rotation.to_dict(),
        }
