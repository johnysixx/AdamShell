class CronenbergMetabolism:

    def __init__(
        self,
        dark_energy_output_rate=0.25
    ):
        self.dark_energy_output_rate = float(
            dark_energy_output_rate
        )

        self.daily_energy_received = 0.0
        self.total_energy_received = 0.0

        self.pending_dark_energy = 0.0
        self.total_dark_energy_produced = 0.0

    def required_daily_energy(
        self,
        size
    ):
        return max(
            1.0,
            float(size)
        )

    def receive_energy(
        self,
        amount,
        size
    ):
        amount = float(amount)
        size = float(size)

        if amount <= 0.0:
            raise ValueError(
                "Cronenberg energy amount "
                "must be positive."
            )

        self.daily_energy_received += amount
        self.total_energy_received += amount

        dark_energy_amount = (
            amount
            * size
            * self.dark_energy_output_rate
        )

        self.pending_dark_energy += (
            dark_energy_amount
        )

        self.total_dark_energy_produced += (
            dark_energy_amount
        )

        return {
            "energy_received": amount,
            "required_energy": (
                self.required_daily_energy(size)
            ),
            "dark_energy_produced": (
                dark_energy_amount
            ),
            "daily_energy_received": (
                self.daily_energy_received
            )
        }

    def is_fed_enough(
        self,
        size
    ):
        return (
            self.daily_energy_received
            >= self.required_daily_energy(size)
        )

    def collect_dark_energy(self):
        amount = self.pending_dark_energy
        self.pending_dark_energy = 0.0

        return amount

    def finish_day(self):
        received = self.daily_energy_received
        self.daily_energy_received = 0.0

        return received

    @property
    def public_state(self):
        return {
            "dark_energy_output_rate": (
                self.dark_energy_output_rate
            ),
            "daily_energy_received": (
                self.daily_energy_received
            ),
            "total_energy_received": (
                self.total_energy_received
            ),
            "pending_dark_energy": (
                self.pending_dark_energy
            ),
            "total_dark_energy_produced": (
                self.total_dark_energy_produced
            )
        }
