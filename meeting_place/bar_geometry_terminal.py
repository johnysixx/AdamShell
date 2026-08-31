from .bar_objects import GeometryStatusSign

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

        self.quantum_layer_map = {
            "tick": None,
            "boxes": [],
            "space": {}
        }

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

        # Ziva mapa se vzdy kompletne prepise
        # soucasnym stavem quantum layer.
        self.quantum_layer_map = {
            "tick": quantum_layer_map.get(
                "tick"
            ),
            "boxes": [
                dict(box)
                for box
                in quantum_layer_map.get(
                    "boxes",
                    []
                )
            ],
            "space": dict(
                quantum_layer_map.get(
                    "space",
                    {}
                )
            )
        }

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
                self.quantum_layer_map
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
