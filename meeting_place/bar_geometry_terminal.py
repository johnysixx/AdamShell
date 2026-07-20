class BarGeometryTerminal:

    def __init__(self):
        self.name = "bar_geometry_terminal"
        self.type = "bar_terminal"

        self.geometry_version = 0
        self.configuration_seed = None

        self.detected_cat_id = None
        self.arrived_cat_id = None

        self.active_quantum_box_count = 0
        self.total_quantum_box_count = 0
        self.total_cat_count = 0

    def update_geometry(
            self,
            geometry_version,
            configuration_seed
    ):
        self.geometry_version = geometry_version
        self.configuration_seed = configuration_seed

    def refresh(self, snapshot):
        geometry = snapshot.get("geometry") or {}
        statistics = snapshot.get("statistics") or {}

        self.geometry_version = (
            geometry.get("geometry_version", 0)
        )

        self.configuration_seed = (
            geometry.get("configuration_seed")
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

    def cat_detected(self, cat_id):
        self.detected_cat_id = cat_id

    def cat_arrived(self, cat_id):
        self.detected_cat_id = None
        self.arrived_cat_id = cat_id

    def display_text(self):
        detected_text = (
            self.detected_cat_id
            if self.detected_cat_id is not None
            else "none"
        )

        arrived_text = (
            self.arrived_cat_id
            if self.arrived_cat_id is not None
            else "none"
        )

        return (
            "CURRENT QUANTUM GEOMETRY\n"
            f"VERSION: {self.geometry_version}\n"
            "STATUS: CURRENT ACTIVE VERSION\n"
            f"QUANTUM BOXES ACTIVE: "
            f"{self.active_quantum_box_count}\n"
            f"QUANTUM BOXES TOTAL: "
            f"{self.total_quantum_box_count}\n"
            f"CATS TOTAL: {self.total_cat_count}\n"
            f"CAT DETECTED: {detected_text}\n"
            f"CAT ARRIVED: {arrived_text}"
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "geometry_version": self.geometry_version,
            "configuration_seed": self.configuration_seed,
            "detected_cat_id": self.detected_cat_id,
            "arrived_cat_id": self.arrived_cat_id,
            "active_quantum_box_count": (
                self.active_quantum_box_count
            ),
            "total_quantum_box_count": (
                self.total_quantum_box_count
            ),
            "total_cat_count": self.total_cat_count,
            "display_text": self.display_text()
        }
