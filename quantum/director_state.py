from dataclasses import dataclass, field


class QuantumDirectorRecord:
    __slots__ = ()


@dataclass(slots=True, frozen=True)
class QuantumDirectorStarCreatedEvent(
    QuantumDirectorRecord
):
    subject: object

    event: str = field(
        default="primordial_idea_star_created",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumDirectorStarExplodedEvent(
    QuantumDirectorRecord
):
    subject: object
    remnant: object

    event: str = field(
        default="primordial_idea_star_exploded",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumDirectorNebulaCreatedEvent(
    QuantumDirectorRecord
):
    subject: object

    event: str = field(
        default="primordial_nebula_created",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumDirectorNebulaStudiedEvent(
    QuantumDirectorRecord
):
    subject: object
    finding: str
    amount: float

    event: str = field(
        default="primordial_nebula_studied",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "finding",
            str(self.finding),
        )

        object.__setattr__(
            self,
            "amount",
            float(self.amount),
        )


@dataclass(slots=True, frozen=True)
class QuantumDirectorMiningMethodInventedEvent(
    QuantumDirectorRecord
):
    subject: object

    invention: str = field(
        default="liquid_hydrocarbon_mining",
        init=False,
    )

    mining_limit_rule: str = field(
        default="maximum_10_percent_of_growth",
        init=False,
    )

    event: str = field(
        default="mining_method_invented",
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumDirectorNebulaMinedEvent(
    QuantumDirectorRecord
):
    subject: object
    mined: float
    miner: str

    material: str = field(
        default="liquid_hydrocarbons",
        init=False,
    )

    event: str = field(
        default="primordial_nebula_mined",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "mined",
            float(self.mined),
        )

        object.__setattr__(
            self,
            "miner",
            str(self.miner),
        )


@dataclass(slots=True, frozen=True)
class QuantumDirectorMaterialSample:
    material: str
    amount: float

    def __post_init__(self):
        object.__setattr__(
            self,
            "material",
            str(self.material),
        )

        object.__setattr__(
            self,
            "amount",
            float(self.amount),
        )

        if self.amount < 0.0:
            raise ValueError(
                "Director material sample amount "
                "cannot be negative."
            )


@dataclass(slots=True, frozen=True)
class QuantumDirectorArrivedAtBarEvent(
    QuantumDirectorRecord
):
    sample: QuantumDirectorMaterialSample
    serpent_present: bool
    met: object | None
    taught_cocktail: str | None

    event: str = field(
        default="director_arrived_at_bar",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.sample,
            QuantumDirectorMaterialSample,
        ):
            raise TypeError(
                "Director bar arrival sample must "
                "be QuantumDirectorMaterialSample."
            )

        object.__setattr__(
            self,
            "serpent_present",
            bool(self.serpent_present),
        )
