LIQUID_HYDROCARBON_FORMATION_THRESHOLD = 10.0

LIQUID_HYDROCARBON_MINING_THRESHOLD = 100.0
class PrimordialNebula:

    def __init__(
        self,
        source_remnants=None
    ):
        self.name = "primordial_nebula"
        self.type = "primordial_nebula"

        self.tick_count = 0
        self.size = 0.0
        self.stars = []

        self.source_remnants = list(
            source_remnants or []
        )

        self.source_remnant_count = len(
            self.source_remnants
        )

        self.elemental_potentials = {}
        self.previous_liquid_hydrocarbon_level = None
        self.current_liquid_hydrocarbon_level = 0.0
        self.mined_from_current_growth = 0.0

        for remnant in self.source_remnants:
            potentials = remnant.get(
                "elemental_potentials",
                {}
            )

            for element, amount in potentials.items():
                self.elemental_potentials[
                    element
                ] = (
                    self.elemental_potentials.get(
                        element,
                        0.0
                    )
                    + amount
                )

        self.state = {
            "name": self.name,
            "type": self.type,
            "size": self.size,
            "stars": self.stars,
            "source_remnants": self.source_remnants,
            "source_remnant_count": (
                self.source_remnant_count
            ),
            "elemental_potentials": self.elemental_potentials
        }

    def form_hydrocarbons(self):
        hydrogen = self.elemental_potentials.get(
            "hydrogen",
            0.0
        )

        carbon = self.elemental_potentials.get(
            "carbon",
            0.0
        )

        if hydrogen <= 0.0 or carbon <= 0.0:
            return 0.0

        amount = min(
            hydrogen,
            carbon
        )

        self.elemental_potentials[
            "hydrocarbons"
        ] = amount

        self.state[
            "elemental_potentials"
        ] = self.elemental_potentials

        return amount

    def can_mine_liquid_hydrocarbons(self):
        return (
            self.size
            >= LIQUID_HYDROCARBON_MINING_THRESHOLD
        )

    def form_liquid_hydrocarbons(self):
        if (
            self.size
            < LIQUID_HYDROCARBON_FORMATION_THRESHOLD
        ):
            return 0.0

        hydrocarbons = self.elemental_potentials.get(
            "hydrocarbons",
            0.0
        )

        if hydrocarbons <= 0.0:
            return 0.0

        self.elemental_potentials[
            "liquid_hydrocarbons"
        ] = hydrocarbons

        self.state[
            "elemental_potentials"
        ] = self.elemental_potentials

        return hydrocarbons

    def record_liquid_hydrocarbon_level(
        self,
        level
    ):
        self.previous_liquid_hydrocarbon_level = (
            self.current_liquid_hydrocarbon_level
        )

        self.current_liquid_hydrocarbon_level = (
            float(level)
        )
        self.mined_from_current_growth = 0.0

        return self.current_liquid_hydrocarbon_level

    def available_liquid_hydrocarbon_mining(self):
        if not self.can_mine_liquid_hydrocarbons():
            return 0.0

        if self.previous_liquid_hydrocarbon_level is None:
            return 0.0

        growth = (
            self.current_liquid_hydrocarbon_level
            - self.previous_liquid_hydrocarbon_level
        )

        if growth <= 0.0:
            return 0.0

        allowed = growth * 0.10

        remaining = (
            allowed
            - self.mined_from_current_growth
        )

        return max(
            0.0,
            remaining
        )

    def mine_liquid_hydrocarbons(
        self,
        amount
    ):
        amount = float(amount)

        if amount <= 0.0:
            raise ValueError(
                "Mining amount must be positive."
            )

        available = (
            self.available_liquid_hydrocarbon_mining()
        )

        if amount > available:
            raise RuntimeError(
                "Liquid hydrocarbon mining limit exceeded."
            )

        self.current_liquid_hydrocarbon_level -= amount

        self.mined_from_current_growth += amount

        return amount

    def tick(self):
        self.tick_count += 1
        return self.tick_count
