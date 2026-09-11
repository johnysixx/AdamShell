from idea_universe.primordial_nebula_state import (
    PrimordialNebulaState,
)


LIQUID_HYDROCARBON_FORMATION_THRESHOLD = 10.0

LIQUID_HYDROCARBON_MINING_THRESHOLD = 100.0


class PrimordialNebula:

    def __init__(
        self,
        source_remnants=None
    ):
        self.name = "primordial_nebula"
        self.type = "primordial_nebula"

        source_remnants = list(
            source_remnants or []
        )

        elemental_potentials = {}

        for remnant in source_remnants:
            potentials = remnant.get(
                "elemental_potentials",
                {}
            )

            for element, amount in potentials.items():
                elemental_potentials[
                    element
                ] = (
                    elemental_potentials.get(
                        element,
                        0.0
                    )
                    + amount
                )

        self.primordial_nebula_state = PrimordialNebulaState(
            source_remnants=source_remnants,
            source_remnant_count=len(source_remnants),
            elemental_potentials=elemental_potentials,
        )
        self.state = self.primordial_nebula_state

    @property
    def tick_count(self):
        return self.primordial_nebula_state.tick_count

    @tick_count.setter
    def tick_count(self, value):
        self.primordial_nebula_state.tick_count = value

    @property
    def size(self):
        return self.primordial_nebula_state.size

    @size.setter
    def size(self, value):
        self.primordial_nebula_state.size = value

    @property
    def stars(self):
        return self.primordial_nebula_state.stars

    @stars.setter
    def stars(self, value):
        self.primordial_nebula_state.stars = value

    @property
    def source_remnants(self):
        return self.primordial_nebula_state.source_remnants

    @source_remnants.setter
    def source_remnants(self, value):
        self.primordial_nebula_state.source_remnants = value

    @property
    def source_remnant_count(self):
        return self.primordial_nebula_state.source_remnant_count

    @source_remnant_count.setter
    def source_remnant_count(self, value):
        self.primordial_nebula_state.source_remnant_count = value

    @property
    def elemental_potentials(self):
        return self.primordial_nebula_state.elemental_potentials

    @elemental_potentials.setter
    def elemental_potentials(self, value):
        self.primordial_nebula_state.elemental_potentials = value

    @property
    def previous_liquid_hydrocarbon_level(self):
        return (
            self
            .primordial_nebula_state
            .previous_liquid_hydrocarbon_level
        )

    @previous_liquid_hydrocarbon_level.setter
    def previous_liquid_hydrocarbon_level(self, value):
        (
            self
            .primordial_nebula_state
            .previous_liquid_hydrocarbon_level
        ) = value

    @property
    def current_liquid_hydrocarbon_level(self):
        return (
            self
            .primordial_nebula_state
            .current_liquid_hydrocarbon_level
        )

    @current_liquid_hydrocarbon_level.setter
    def current_liquid_hydrocarbon_level(self, value):
        (
            self
            .primordial_nebula_state
            .current_liquid_hydrocarbon_level
        ) = value

    @property
    def mined_from_current_growth(self):
        return (
            self
            .primordial_nebula_state
            .mined_from_current_growth
        )

    @mined_from_current_growth.setter
    def mined_from_current_growth(self, value):
        (
            self
            .primordial_nebula_state
            .mined_from_current_growth
        ) = value

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            **self.primordial_nebula_state.to_dict(),
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
