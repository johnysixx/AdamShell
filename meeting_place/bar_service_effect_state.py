from dataclasses import dataclass, field


def _normalize_entity(
    value,
):
    if value is None:
        return None

    return str(
        value
    )


@dataclass(slots=True, frozen=True)
class BarGodEnergyDrinkEffect:
    entity: str | None
    existence_cost_pct: float
    creative_will_gain: float

    name: str = field(
        default="god_energy_drink_effect",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "entity",
            _normalize_entity(
                self.entity
            ),
        )

        object.__setattr__(
            self,
            "existence_cost_pct",
            float(
                self.existence_cost_pct
            ),
        )

        object.__setattr__(
            self,
            "creative_will_gain",
            float(
                self.creative_will_gain
            ),
        )


@dataclass(slots=True, frozen=True)
class BarIdeaEntityEnergyDrinkEffect:
    entity: str | None
    existence_cost_pct: float
    will_gain: float

    name: str = field(
        default=(
            "idea_entity_energy_drink_effect"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "entity",
            _normalize_entity(
                self.entity
            ),
        )

        object.__setattr__(
            self,
            "existence_cost_pct",
            float(
                self.existence_cost_pct
            ),
        )

        object.__setattr__(
            self,
            "will_gain",
            float(
                self.will_gain
            ),
        )


@dataclass(slots=True, frozen=True)
class BarEnergyDrinkUnavailableResult:
    entity: str | None
    entity_type: str | None

    name: str = field(
        default="energy_drink_not_available",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "entity",
            _normalize_entity(
                self.entity
            ),
        )

        object.__setattr__(
            self,
            "entity_type",
            _normalize_entity(
                self.entity_type
            ),
        )


@dataclass(slots=True, frozen=True)
class BarGodEntropyDrinkEffect:
    entity: str | None
    existence_gain_pct: float
    entity_energy_gain_j: float
    payment_pct: float

    name: str = field(
        default="god_entropy_drink_effect",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "entity",
            _normalize_entity(
                self.entity
            ),
        )

        object.__setattr__(
            self,
            "existence_gain_pct",
            float(
                self.existence_gain_pct
            ),
        )

        object.__setattr__(
            self,
            "entity_energy_gain_j",
            float(
                self.entity_energy_gain_j
            ),
        )

        object.__setattr__(
            self,
            "payment_pct",
            float(
                self.payment_pct
            ),
        )


@dataclass(slots=True, frozen=True)
class BarIdeaEntityEntropyDrinkEffect:
    entity: str | None
    entity_energy_gain_j: float
    payment_pct: float

    name: str = field(
        default=(
            "idea_entity_entropy_drink_effect"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "entity",
            _normalize_entity(
                self.entity
            ),
        )

        object.__setattr__(
            self,
            "entity_energy_gain_j",
            float(
                self.entity_energy_gain_j
            ),
        )

        object.__setattr__(
            self,
            "payment_pct",
            float(
                self.payment_pct
            ),
        )


@dataclass(slots=True, frozen=True)
class BarEntropyDrinkUnavailableResult:
    entity: str | None
    entity_type: str | None

    name: str = field(
        default="entropy_drink_not_available",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "entity",
            _normalize_entity(
                self.entity
            ),
        )

        object.__setattr__(
            self,
            "entity_type",
            _normalize_entity(
                self.entity_type
            ),
        )
