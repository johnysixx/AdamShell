import math


class CronenbergHunger:

    def __init__(
        self,
        starvation_threshold_days=1,
        minimum_digestion_days=2,
        maximum_digestion_days=7
    ):
        self.starvation_threshold_days = int(
            starvation_threshold_days
        )

        self.minimum_digestion_days = int(
            minimum_digestion_days
        )

        self.maximum_digestion_days = int(
            maximum_digestion_days
        )

        self.hungry_days = 0
        self.satiety_days_remaining = 0

        self.last_consumed_mass = 0.0
        self.last_digestion_days = 0

    @property
    def is_satiated(self):
        return (
            self.satiety_days_remaining
            > 0
        )

    @property
    def is_hungry(self):
        return (
            not self.is_satiated
            and self.hungry_days > 0
        )

    @property
    def can_hunt(self):
        return (
            not self.is_satiated
            and self.hungry_days
            >= self.starvation_threshold_days
        )

    def calculate_digestion_days(
        self,
        consumed_mass
    ):
        consumed_mass = max(
            0.0,
            float(consumed_mass)
        )

        digestion_days = (
            1
            + math.ceil(
                consumed_mass / 2.0
            )
        )

        return min(
            self.maximum_digestion_days,
            max(
                self.minimum_digestion_days,
                digestion_days
            )
        )

    def finish_day(
        self,
        fed_enough
    ):
        if self.is_satiated:
            self.satiety_days_remaining -= 1
            self.hungry_days = 0

            return {
                "state": "digesting",
                "hungry_days": 0,
                "satiety_days_remaining": (
                    self.satiety_days_remaining
                ),
                "can_hunt": False
            }

        if fed_enough:
            self.hungry_days = 0

            return {
                "state": "fed",
                "hungry_days": 0,
                "satiety_days_remaining": 0,
                "can_hunt": False
            }

        self.hungry_days += 1

        return {
            "state": "hungry",
            "hungry_days": self.hungry_days,
            "satiety_days_remaining": 0,
            "can_hunt": self.can_hunt
        }

    def start_digestion(
        self,
        consumed_mass
    ):
        consumed_mass = float(
            consumed_mass
        )

        digestion_days = (
            self.calculate_digestion_days(
                consumed_mass
            )
        )

        self.last_consumed_mass = (
            consumed_mass
        )

        self.last_digestion_days = (
            digestion_days
        )

        self.satiety_days_remaining = (
            digestion_days
        )

        self.hungry_days = 0

        return {
            "state": "digesting",
            "consumed_mass": consumed_mass,
            "digestion_days": digestion_days,
            "satiety_days_remaining": (
                self.satiety_days_remaining
            )
        }

    @property
    def public_state(self):
        return {
            "starvation_threshold_days": (
                self.starvation_threshold_days
            ),
            "minimum_digestion_days": (
                self.minimum_digestion_days
            ),
            "maximum_digestion_days": (
                self.maximum_digestion_days
            ),
            "hungry_days": self.hungry_days,
            "satiety_days_remaining": (
                self.satiety_days_remaining
            ),
            "last_consumed_mass": (
                self.last_consumed_mass
            ),
            "last_digestion_days": (
                self.last_digestion_days
            ),
            "is_satiated": self.is_satiated,
            "is_hungry": self.is_hungry,
            "can_hunt": self.can_hunt
        }
