import uuid
from dataclasses import dataclass

from core.entity.components import SpatialVector3


@dataclass(slots=True, frozen=True)
class QuantumCatRouteDetour:
    blocked_position: SpatialVector3
    detour_position: SpatialVector3
    returns_to_original_route: bool
    destination: str

    def __post_init__(self):
        if not isinstance(self.blocked_position, SpatialVector3):
            raise TypeError(
                "Quantum cat route detour blocked_position must be a SpatialVector3 object."
            )
        if not isinstance(self.detour_position, SpatialVector3):
            raise TypeError(
                "Quantum cat route detour detour_position must be a SpatialVector3 object."
            )

    def to_dict(self):
        return {
            "blocked_position": self.blocked_position.to_dict(),
            "detour_position": self.detour_position.to_dict(),
            "returns_to_original_route": self.returns_to_original_route,
            "destination": self.destination,
        }


@dataclass(slots=True, frozen=True)
class QuantumCatRouteEncounter:
    result: str
    encountered: bool | None = None
    cat: str | None = None
    cronenberg: str | None = None
    blocked_by: str | None = None
    position: SpatialVector3 | None = None
    size_ratio: float | None = None
    escape_chance: float | None = None
    detour: SpatialVector3 | None = None
    destination: str | None = None
    cat_growth: float | None = None
    strength_gain: float | None = None
    subscriber_count: int | None = None

    def __post_init__(self):
        for field_name in (
            "position",
            "detour",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                value is not None
                and not isinstance(
                    value,
                    SpatialVector3,
                )
            ):
                raise TypeError(
                    f"Quantum cat route encounter {field_name} "
                    "must be a SpatialVector3 object."
                )

    def to_dict(self):
        snapshot = {
            "result": self.result,
        }

        for field_name in (
            "encountered",
            "cat",
            "cronenberg",
            "blocked_by",
            "size_ratio",
            "escape_chance",
            "destination",
            "cat_growth",
            "strength_gain",
            "subscriber_count",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                snapshot[field_name] = value

        if self.position is not None:
            snapshot["position"] = (
                self.position.to_dict()
            )

        if self.detour is not None:
            snapshot["detour"] = (
                self.detour.to_dict()
            )

        return snapshot


class QuantumCatRoute:

    def __init__(
        self,
        cat_id,
        route_steps,
        start_position,
        destination="bar_front_door"
    ):
        self.route_id = (
            f"cat_route_"
            f"{uuid.uuid4().hex[:8]}"
        )

        self.cat_id = cat_id
        self.destination = destination

        self.route_steps = [
            self._require_position(
                step,
                field_name="route step",
            )
            for step in route_steps
        ]

        self.start_position = self._require_position(
            start_position,
            field_name="start position",
        )

        self.current_step_index = 0
        self.current_position = self.start_position

        self.detours = []
        self.encounters = []

        self.memory_started = False

        self.state = "observed"
        self.observation_active = True

    @staticmethod
    def _require_position(position, field_name):
        if not isinstance(position, SpatialVector3):
            raise TypeError(
                f"Quantum cat route {field_name} must be a SpatialVector3 object."
            )
        return position

    @property
    def next_position(self):
        if (
            self.current_step_index
            >= len(self.route_steps)
        ):
            return None

        return self.route_steps[
            self.current_step_index
        ]

    @property
    def has_arrived(self):
        return self.next_position is None

    def position_matches(
        self,
        position,
        tolerance=0.001
    ):
        position = self._require_position(
            position,
            field_name="comparison position",
        )

        next_position = self.next_position

        if next_position is None:
            return False

        return (
            abs(next_position.x - position.x) <= tolerance
            and abs(next_position.y - position.y) <= tolerance
            and abs(next_position.z - position.z) <= tolerance
        )

    def advance(self):
        next_position = self.next_position

        if next_position is None:
            self.state = "arrived"
            self.stop_observation()
            return None

        self.current_position = next_position
        self.current_step_index += 1

        if self.has_arrived:
            self.state = "arrived"
            self.stop_observation()
        else:
            self.state = "travelling"

        return self.current_position

    def detour_count_for(self, blocked_position):
        if blocked_position is None:
            return 0

        blocked_position = self._require_position(
            blocked_position,
            field_name="blocked position",
        )

        return sum(
            1
            for detour in self.detours
            if detour.blocked_position == blocked_position
        )

    def make_minimal_detour(
        self,
        blocked_position,
        clearance=0.25
    ):
        blocked_position = self._require_position(
            blocked_position,
            field_name="blocked position",
        )

        detour_position = SpatialVector3(
            x=blocked_position.x,
            y=blocked_position.y + float(clearance),
            z=blocked_position.z,
        )

        self.detours.append(
            QuantumCatRouteDetour(
                blocked_position=blocked_position,
                detour_position=detour_position,
                returns_to_original_route=True,
                destination=self.destination,
            )
        )

        self.current_position = detour_position
        self.state = "avoiding_obstacle"

        return detour_position

    def record_encounter(
        self,
        encounter
    ):
        if not isinstance(
            encounter,
            QuantumCatRouteEncounter,
        ):
            raise TypeError(
                "Quantum cat route encounter must be "
                "a QuantumCatRouteEncounter object."
            )

        self.encounters.append(
            encounter
        )

        return encounter

    def stop_observation(self):
        self.observation_active = False
        self.state = "released"

    @property
    def public_state(self):
        return {
            "type": "quantum_cat_route",
            "route_id": self.route_id,
            "cat_id": self.cat_id,
            "destination": self.destination,
            "route_steps": [
                step.to_dict()
                for step in self.route_steps
            ],
            "start_position": self.start_position.to_dict(),
            "current_position": self.current_position.to_dict(),
            "current_step_index": self.current_step_index,
            "next_position": (
                None
                if self.next_position is None
                else self.next_position.to_dict()
            ),
            "has_arrived": self.has_arrived,
            "detours": [
                detour.to_dict()
                for detour in self.detours
            ],
            "encounters": [
                encounter.to_dict()
                for encounter in self.encounters
            ],
            "state": self.state,
            "observation_active": self.observation_active,
        }
