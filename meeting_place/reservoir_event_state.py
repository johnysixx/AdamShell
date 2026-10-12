from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class BarEnergyAddedEvent:
    source: str
    amount_j: float
    total_energy_j: float

    name: str = field(
        default="bar_energy_added",
        init=False,
    )

    def __post_init__(self):
        amount_j = float(
            self.amount_j
        )

        total_energy_j = float(
            self.total_energy_j
        )

        if amount_j <= 0.0:
            raise ValueError(
                "Added bar energy must be positive."
            )

        if total_energy_j < 0.0:
            raise ValueError(
                "Total bar energy cannot be negative."
            )

        object.__setattr__(
            self,
            "source",
            str(self.source),
        )

        object.__setattr__(
            self,
            "amount_j",
            amount_j,
        )

        object.__setattr__(
            self,
            "total_energy_j",
            total_energy_j,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "source": self.source,
            "amount_j": self.amount_j,
            "total_energy_j":
                self.total_energy_j,
        }


@dataclass(slots=True, frozen=True)
class BarEnergySpentEvent:
    purpose: str
    amount_j: float
    total_energy_j: float

    name: str = field(
        default="bar_energy_spent",
        init=False,
    )

    def __post_init__(self):
        amount_j = float(
            self.amount_j
        )

        total_energy_j = float(
            self.total_energy_j
        )

        if amount_j <= 0.0:
            raise ValueError(
                "Spent bar energy must be positive."
            )

        if total_energy_j < 0.0:
            raise ValueError(
                "Total bar energy cannot be negative."
            )

        object.__setattr__(
            self,
            "purpose",
            str(self.purpose),
        )

        object.__setattr__(
            self,
            "amount_j",
            amount_j,
        )

        object.__setattr__(
            self,
            "total_energy_j",
            total_energy_j,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "purpose": self.purpose,
            "amount_j": self.amount_j,
            "total_energy_j":
                self.total_energy_j,
        }


@dataclass(slots=True, frozen=True)
class QuantumEntropyTickEvent:
    amount_units: float
    total_entropy_units: float

    name: str = field(
        default="quantum_entropy_tick",
        init=False,
    )

    def __post_init__(self):
        amount_units = float(
            self.amount_units
        )

        total_entropy_units = float(
            self.total_entropy_units
        )

        if amount_units < 0.0:
            raise ValueError(
                "Quantum entropy tick cannot "
                "add negative entropy."
            )

        if total_entropy_units < 0.0:
            raise ValueError(
                "Total bar entropy cannot be negative."
            )

        object.__setattr__(
            self,
            "amount_units",
            amount_units,
        )

        object.__setattr__(
            self,
            "total_entropy_units",
            total_entropy_units,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "amount_units":
                self.amount_units,
            "total_entropy_units":
                self.total_entropy_units,
        }


@dataclass(slots=True, frozen=True)
class BarEntropyAddedEvent:
    source: str
    amount_units: float
    total_entropy_units: float

    name: str = field(
        default="bar_entropy_added",
        init=False,
    )

    def __post_init__(self):
        amount_units = float(
            self.amount_units
        )

        total_entropy_units = float(
            self.total_entropy_units
        )

        if amount_units <= 0.0:
            raise ValueError(
                "Added bar entropy must be positive."
            )

        if total_entropy_units < 0.0:
            raise ValueError(
                "Total bar entropy cannot be negative."
            )

        object.__setattr__(
            self,
            "source",
            str(self.source),
        )

        object.__setattr__(
            self,
            "amount_units",
            amount_units,
        )

        object.__setattr__(
            self,
            "total_entropy_units",
            total_entropy_units,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "source": self.source,
            "amount_units":
                self.amount_units,
            "total_entropy_units":
                self.total_entropy_units,
        }


@dataclass(slots=True, frozen=True)
class EntropyServedEvent:
    drinker: str
    entropy_units_spent: float
    bar_energy_gain_j: float
    entity_energy_gain_j: float
    total_entropy_units: float

    name: str = field(
        default="entropy_served",
        init=False,
    )

    def __post_init__(self):
        entropy_units_spent = float(
            self.entropy_units_spent
        )

        bar_energy_gain_j = float(
            self.bar_energy_gain_j
        )

        entity_energy_gain_j = float(
            self.entity_energy_gain_j
        )

        total_entropy_units = float(
            self.total_entropy_units
        )

        if entropy_units_spent <= 0.0:
            raise ValueError(
                "Served entropy amount must be positive."
            )

        if (
            bar_energy_gain_j < 0.0
            or entity_energy_gain_j < 0.0
            or total_entropy_units < 0.0
        ):
            raise ValueError(
                "Entropy service energy and totals "
                "cannot be negative."
            )

        object.__setattr__(
            self,
            "drinker",
            str(self.drinker),
        )

        object.__setattr__(
            self,
            "entropy_units_spent",
            entropy_units_spent,
        )

        object.__setattr__(
            self,
            "bar_energy_gain_j",
            bar_energy_gain_j,
        )

        object.__setattr__(
            self,
            "entity_energy_gain_j",
            entity_energy_gain_j,
        )

        object.__setattr__(
            self,
            "total_entropy_units",
            total_entropy_units,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "drinker": self.drinker,
            "entropy_units_spent":
                self.entropy_units_spent,
            "bar_energy_gain_j":
                self.bar_energy_gain_j,
            "entity_energy_gain_j":
                self.entity_energy_gain_j,
            "total_entropy_units":
                self.total_entropy_units,
        }
