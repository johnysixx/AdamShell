from universe.logger import UniverseLogger


class BottleShelf:

    def __init__(self):
        self.name = "bottle_shelf"
        self.location = "behind_bar"
        self.bottles = []

        UniverseLogger.boot(
            "BOTTLE SHELF CREATED BEHIND BAR"
        )

    def add_dark_energy(
        self,
        amount_j
    ):
        amount_j = float(
            amount_j
        )

        if amount_j <= 0.0:
            raise ValueError(
                "Dark energy amount must be positive."
            )

        existing = next(
            (
                bottle
                for bottle in self.bottles
                if bottle.get("type")
                == "dark_energy_bottle"
            ),
            None
        )

        if existing is not None:
            existing["dark_energy_j"] += (
                amount_j
            )

            UniverseLogger.event(
                "DARK ENERGY BOTTLE FILLED: "
                f"+{amount_j:.3f} J "
                f"TOTAL="
                f"{existing['dark_energy_j']:.3f} J"
            )

            return existing

        bottle = {
            "name": "dark_energy_bottle",
            "type": "dark_energy_bottle",
            "location": self.name,
            "dark_energy_j": amount_j
        }

        self.bottles.append(
            bottle
        )

        UniverseLogger.event(
            "DARK ENERGY BOTTLE CREATED: "
            f"{amount_j:.3f} J"
        )

        return bottle

