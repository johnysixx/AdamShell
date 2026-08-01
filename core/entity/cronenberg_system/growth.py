class CronenbergGrowth:

    def __init__(
        self,
        fed_growth=0.25,
        layer_growth=0.10,
        starvation_mass_loss=0.10,
        starvation_loss_starts_day=2,
        minimum_size=0.50
    ):
        self.fed_growth = float(
            fed_growth
        )

        self.layer_growth = float(
            layer_growth
        )

        self.starvation_mass_loss = float(
            starvation_mass_loss
        )

        self.starvation_loss_starts_day = int(
            starvation_loss_starts_day
        )

        self.minimum_size = float(
            minimum_size
        )

        self.total_growth = 0.0
        self.total_mass_consumed = 0.0
        self.total_mass_lost = 0.0

    def grow_from_feeding(
        self,
        size
    ):
        old_size = float(size)
        new_size = (
            old_size
            + self.fed_growth
        )

        self.total_growth += (
            self.fed_growth
        )

        return {
            "cause": "feeding",
            "old_size": old_size,
            "new_size": new_size,
            "growth": self.fed_growth
        }

    def grow_from_layer(
        self,
        size
    ):
        old_size = float(size)
        new_size = (
            old_size
            + self.layer_growth
        )

        self.total_growth += (
            self.layer_growth
        )

        return {
            "cause": "layer_crossing",
            "old_size": old_size,
            "new_size": new_size,
            "growth": self.layer_growth
        }

    def apply_starvation(
        self,
        size,
        hungry_days
    ):
        old_size = float(size)
        hungry_days = int(hungry_days)

        if (
            hungry_days
            < self.starvation_loss_starts_day
        ):
            return {
                "cause": "starvation",
                "old_size": old_size,
                "new_size": old_size,
                "mass_lost": 0.0
            }

        new_size = max(
            self.minimum_size,
            old_size
            - self.starvation_mass_loss
        )

        mass_lost = (
            old_size
            - new_size
        )

        self.total_mass_lost += (
            mass_lost
        )

        return {
            "cause": "starvation",
            "old_size": old_size,
            "new_size": new_size,
            "mass_lost": mass_lost
        }

    def absorb_mass(
        self,
        size,
        consumed_mass
    ):
        old_size = float(size)
        consumed_mass = max(
            0.0,
            float(consumed_mass)
        )

        new_size = (
            old_size
            + consumed_mass
        )

        self.total_mass_consumed += (
            consumed_mass
        )

        return {
            "cause": "consumption",
            "old_size": old_size,
            "new_size": new_size,
            "mass_gained": consumed_mass
        }

    @property
    def public_state(self):
        return {
            "fed_growth": self.fed_growth,
            "layer_growth": self.layer_growth,
            "starvation_mass_loss": (
                self.starvation_mass_loss
            ),
            "starvation_loss_starts_day": (
                self.starvation_loss_starts_day
            ),
            "minimum_size": self.minimum_size,
            "total_growth": self.total_growth,
            "total_mass_consumed": (
                self.total_mass_consumed
            ),
            "total_mass_lost": (
                self.total_mass_lost
            )
        }
