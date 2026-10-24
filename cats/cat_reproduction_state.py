from cats.cat_development_stage import CatDevelopmentStage
from dataclasses import dataclass, field

from cats.cat_birth_objects import (
    CatLitter,
    KittenEmbryo,
)
from cats.cat_estrous_phase import CatEstrousPhase

from cats.mating_contact import CatMatingContact




@dataclass(slots=True)
class CatReproductionState:

    sex: str
    neutered: bool = False
    fertile: bool = field(init=False)

    developmental_stage: CatDevelopmentStage | None = None
    reproductive_maturity: bool = False

    estrous_phase: CatEstrousPhase = CatEstrousPhase.INACTIVE
    estrus_active: bool = False
    estrous_cycle_day: int = 0
    estrus_duration_days: int = 7
    interestrus_duration_days: int = 8
    estrous_cycles_completed: int = 0

    mating_window_open: bool = False
    mating_window_started_day: int | None = None
    mating_contacts: list[CatMatingContact] = field(default_factory=list)
    potential_fathers: list[str] = field(default_factory=list)

    ovulation_stimulation: int = 0
    ovulation_threshold: int = 4
    ovulation_induced: bool = False
    last_ovulation_day: int | None = None

    pregnant: bool = False
    pregnancy_day: int | None = None
    gestation_days: int | None = None
    expected_birth_day: int | None = None

    mother_name: str | None = None

    embryos: list[KittenEmbryo] = field(default_factory=list)
    litters: list[CatLitter] = field(default_factory=list)
    last_litter: CatLitter | None = None
    litters_born: int = 0

    def __post_init__(self):
        if self.sex not in {"female", "male"}:
            raise ValueError(
                "Cat reproductive sex must be female or male."
            )

        self.neutered = bool(self.neutered)
        self.fertile = not self.neutered
