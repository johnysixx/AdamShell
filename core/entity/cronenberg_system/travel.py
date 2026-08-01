class CronenbergTravel:

    def __init__(
        self,
        layer_growth=0.10,
        energy_cost_rate=0.05,
        minimum_energy_cost=0.10,
        dark_energy_output_rate=0.25
    ):
        self.layer_growth = float(
            layer_growth
        )

        self.energy_cost_rate = float(
            energy_cost_rate
        )

        self.minimum_energy_cost = float(
            minimum_energy_cost
        )

        self.dark_energy_output_rate = float(
            dark_energy_output_rate
        )

        self.layers_crossed = 0
        self.travel_steps = 0

        self.total_energy_consumed = 0.0
        self.total_dark_energy_produced = 0.0

    def cross_layer(
        self,
        size
    ):
        new_size = (
            float(size)
            + self.layer_growth
        )

        self.layers_crossed += 1

        return {
            "old_size": float(size),
            "new_size": new_size,
            "growth": self.layer_growth,
            "layers_crossed": (
                self.layers_crossed
            )
        }

    def travel_step(
        self,
        size,
        available_energy
    ):
        size = float(size)
        available_energy = float(
            available_energy
        )

        energy_cost = max(
            self.minimum_energy_cost,
            size * self.energy_cost_rate
        )

        energy_spent = min(
            available_energy,
            energy_cost
        )

        dark_energy = (
            energy_spent
            * size
            * self.dark_energy_output_rate
        )

        self.travel_steps += 1
        self.total_energy_consumed += (
            energy_spent
        )

        self.total_dark_energy_produced += (
            dark_energy
        )

        return {
            "energy_cost": energy_cost,
            "energy_spent": energy_spent,
            "dark_energy_produced": (
                dark_energy
            ),
            "travel_steps": (
                self.travel_steps
            )
        }

    def cat_response(
        self,
        size
    ):
        size = float(size)

        if size < 1.75:
            return "hunt"

        if size < 3.0:
            return "observe"

        return "avoid"

    @property
    def public_state(self):
        return {
            "layer_growth": self.layer_growth,
            "energy_cost_rate": (
                self.energy_cost_rate
            ),
            "minimum_energy_cost": (
                self.minimum_energy_cost
            ),
            "dark_energy_output_rate": (
                self.dark_energy_output_rate
            ),
            "layers_crossed": (
                self.layers_crossed
            ),
            "travel_steps": (
                self.travel_steps
            ),
            "total_energy_consumed": (
                self.total_energy_consumed
            ),
            "total_dark_energy_produced": (
                self.total_dark_energy_produced
            )
        }
