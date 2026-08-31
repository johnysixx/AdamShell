from universe.logger import UniverseLogger
from meeting_place.bar_objects import DarkEnergyBottle


class BottleShelf:

    def __init__(self):
        self.name = "bottle_shelf"
        self.location = "behind_bar"
        self.bottles = []
        UniverseLogger.boot("BOTTLE SHELF CREATED BEHIND BAR")

    def add_dark_energy(self, amount_j):
        amount_j = float(amount_j)
        if amount_j <= 0.0:
            raise ValueError("Dark energy amount must be positive.")
        existing = next(
            (
                bottle
                for bottle in self.bottles
                if bottle.type == "dark_energy_bottle"
            ),
            None,
        )
        if existing is not None:
            existing.add_energy(amount_j)
            UniverseLogger.event(
                "DARK ENERGY BOTTLE FILLED: "
                f"+{amount_j:.3f} J "
                f"TOTAL={existing.dark_energy_j:.3f} J"
            )
            return existing
        bottle = DarkEnergyBottle(
            name="dark_energy_bottle",
            type="dark_energy_bottle",
            location=self.name,
            dark_energy_j=amount_j,
        )
        self.bottles.append(bottle)
        UniverseLogger.event(
            "DARK ENERGY BOTTLE CREATED: "
            f"{amount_j:.3f} J"
        )
        return bottle
