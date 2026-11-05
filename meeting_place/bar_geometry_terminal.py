from copy import deepcopy
from dataclasses import dataclass, field

from .bar_objects import GeometryStatusSign

@dataclass(slots=True)
class BarQuantumLayerMapState:
    tick: int | None = None
    boxes: tuple = ()
    space: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.boxes, tuple):
            raise TypeError(
                "Quantum map boxes must be a tuple."
            )

        if not all(
            isinstance(box, dict)
            for box in self.boxes
        ):
            raise TypeError(
                "Quantum map requires serialized box snapshots."
            )

        if not isinstance(self.space, dict):
            raise TypeError(
                "Quantum map space snapshot must be a dictionary."
            )

        self.boxes = tuple(
            deepcopy(box)
            for box in self.boxes
        )

        self.space = deepcopy(self.space)

    @classmethod
    def from_snapshot(cls, snapshot):
        if not isinstance(snapshot, dict):
            raise TypeError(
                "Quantum map input must be a snapshot."
            )

        boxes = snapshot.get("boxes", [])

        if not isinstance(boxes, (list, tuple)):
            raise TypeError(
                "Quantum map box snapshots must be a sequence."
            )

        return cls(
            tick=snapshot.get("tick"),
            boxes=tuple(boxes),
            space=snapshot.get("space", {}),
        )

    def to_dict(self):
        return {
            "tick": self.tick,
            "boxes": deepcopy(
                list(self.boxes)
            ),
            "space": deepcopy(
                self.space
            ),
        }


class BarGeometryTerminal:

    def __init__(self):
        self.name = "bar_geometry_terminal"
        self.type = "bar_terminal"

        self.location = "bar_wall"
        self.display_mode = "live_quantum_layer_map"

        self.geometry_version = 0
        self.configuration_seed = None

        self.detected_cat_id = None
        self.arrived_cat_id = None

        self.status_sign = GeometryStatusSign(
            name="cat_arrival_status_sign",
            type="illuminated_bar_wall_sign",
            location="bar_wall_next_to_quantum_map",
            cat_detected_light=False,
            cat_arrived_light=False
        )

        self.active_quantum_box_count = 0
        self.total_quantum_box_count = 0
        self.total_cat_count = 0

        self.quantum_layer_map = (
            BarQuantumLayerMapState()
        )

    def update_geometry(
        self,
        geometry_version,
        configuration_seed
    ):
        self.geometry_version = geometry_version
        self.configuration_seed = (
            configuration_seed
        )

    def refresh(
        self,
        snapshot
    ):
        geometry = (
            snapshot.get(
                "geometry"
            )
            or {}
        )

        statistics = (
            snapshot.get(
                "statistics"
            )
            or {}
        )

        quantum_layer_map = (
            snapshot.get(
                "quantum_layer_map"
            )
            or {}
        )

        self.geometry_version = (
            geometry.get(
                "geometry_version",
                0
            )
        )

        self.configuration_seed = (
            geometry.get(
                "configuration_seed"
            )
        )

        self.active_quantum_box_count = (
            statistics.get(
                "active_quantum_box_count",
                0
            )
        )

        self.total_quantum_box_count = (
            statistics.get(
                "total_quantum_boxes_created",
                0
            )
        )

        self.total_cat_count = (
            statistics.get(
                "total_cats_created",
                0
            )
        )

        # Replace the previous map with a detached
        # typed state built from the current snapshot.
        self.quantum_layer_map = (
            BarQuantumLayerMapState.from_snapshot(
                quantum_layer_map
            )
        )

    def cat_detected(
        self,
        cat_id
    ):
        self.detected_cat_id = cat_id
        self.arrived_cat_id = None

        self.status_sign.cat_detected_light = True

        self.status_sign.cat_arrived_light = False

    def cat_arrived(
        self,
        cat_id
    ):
        self.detected_cat_id = None
        self.arrived_cat_id = cat_id

        self.status_sign.cat_detected_light = False

        self.status_sign.cat_arrived_light = True

    def display_text(self):
        return (
            "CURRENT QUANTUM LAYER\n"
            f"VERSION: {self.geometry_version}\n"
            "STATUS: CURRENT ACTIVE VERSION\n"
            f"QUANTUM BOXES ACTIVE: "
            f"{self.active_quantum_box_count}\n"
            f"QUANTUM BOXES TOTAL: "
            f"{self.total_quantum_box_count}"
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "display_mode": self.display_mode,
            "geometry_version": (
                self.geometry_version
            ),
            "configuration_seed": (
                self.configuration_seed
            ),
            "quantum_layer_map": (
                self.quantum_layer_map.to_dict()
            ),
            "status_sign": self.status_sign.to_dict(),
            "detected_cat_id": (
                self.detected_cat_id
            ),
            "arrived_cat_id": (
                self.arrived_cat_id
            ),
            "active_quantum_box_count": (
                self.active_quantum_box_count
            ),
            "total_quantum_box_count": (
                self.total_quantum_box_count
            ),
            "total_cat_count": (
                self.total_cat_count
            ),
            "display_text": self.display_text()
        }
