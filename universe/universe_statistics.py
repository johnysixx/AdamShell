class UniverseStatistics:

    def __init__(self):
        self.name = "universe_statistics"
        self.type = "statistics"

        self.total_quantum_boxes_created = 0
        self.total_quantum_boxes_disappeared = 0

        self.total_cats_created = 0
        self.total_cat_arrivals = 0

        self.total_quantum_collapses = 0
        self.total_geometry_reconfigurations = 0
        self.total_dice_rolls = 0

    def record_quantum_box_created(self):
        self.total_quantum_boxes_created += 1

    def record_quantum_box_disappeared(self):
        self.total_quantum_boxes_disappeared += 1

    def record_cat_created(self):
        self.total_cats_created += 1

    def record_cat_arrived(self):
        self.total_cat_arrivals += 1

    def record_quantum_collapse(self):
        self.total_quantum_collapses += 1

    def record_geometry_reconfiguration(self):
        self.total_geometry_reconfigurations += 1

    def record_dice_roll(self):
        self.total_dice_rolls += 1

    @property
    def active_quantum_box_count(self):
        return max(
            self.total_quantum_boxes_created
            - self.total_quantum_boxes_disappeared,
            0
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "active_quantum_box_count": (
                self.active_quantum_box_count
            ),
            "total_quantum_boxes_created": (
                self.total_quantum_boxes_created
            ),
            "total_quantum_boxes_disappeared": (
                self.total_quantum_boxes_disappeared
            ),
            "total_cats_created": self.total_cats_created,
            "total_cat_arrivals": self.total_cat_arrivals,
            "total_quantum_collapses": (
                self.total_quantum_collapses
            ),
            "total_geometry_reconfigurations": (
                self.total_geometry_reconfigurations
            ),
            "total_dice_rolls": self.total_dice_rolls
        }
