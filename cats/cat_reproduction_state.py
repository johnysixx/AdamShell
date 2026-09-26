from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True)
class CatReproductionState:

    sex: str
    neutered: bool = False
    fertile: bool = field(init=False)

    developmental_stage: str | None = None
    reproductive_maturity: bool = False

    estrous_phase: str = "inactive"
    estrus_active: bool = False
    estrous_cycle_day: int = 0
    estrus_duration_days: int = 7
    interestrus_duration_days: int = 8
    estrous_cycles_completed: int = 0

    mating_window_open: bool = False
    mating_window_started_day: int | None = None
    mating_contacts: list = field(default_factory=list)
    potential_fathers: list = field(default_factory=list)

    ovulation_stimulation: int = 0
    ovulation_threshold: int = 4
    ovulation_induced: bool = False
    last_ovulation_day: int | None = None

    pregnant: bool = False
    pregnancy_day: int | None = None
    gestation_days: int | None = None
    expected_birth_day: int | None = None

    mother_name: str | None = None
    father_name: str | None = None
    father_names: list = field(default_factory=list)
    mating_contact: object | None = None

    embryos: list = field(default_factory=list)
    litters: list = field(default_factory=list)
    last_litter: object | None = None
    litters_born: int = 0

    def __post_init__(self):
        if self.sex not in {"female", "male"}:
            raise ValueError(
                "Cat reproductive sex must be female or male."
            )

        self.neutered = bool(self.neutered)
        self.fertile = not self.neutered

    def to_dict(self):
        return {
            "sex": self.sex,
            "neutered": self.neutered,
            "fertile": self.fertile,
            "developmental_stage": self.developmental_stage,
            "reproductive_maturity": self.reproductive_maturity,
            "estrous_phase": self.estrous_phase,
            "estrus_active": self.estrus_active,
            "estrous_cycle_day": self.estrous_cycle_day,
            "estrus_duration_days": self.estrus_duration_days,
            "interestrus_duration_days": self.interestrus_duration_days,
            "estrous_cycles_completed": self.estrous_cycles_completed,
            "mating_window_open": self.mating_window_open,
            "mating_window_started_day": self.mating_window_started_day,
            "mating_contacts": [
                contact.to_dict()
                for contact
                in self.mating_contacts
            ],
            "potential_fathers": list(self.potential_fathers),
            "ovulation_stimulation": self.ovulation_stimulation,
            "ovulation_threshold": self.ovulation_threshold,
            "ovulation_induced": self.ovulation_induced,
            "last_ovulation_day": self.last_ovulation_day,
            "pregnant": self.pregnant,
            "pregnancy_day": self.pregnancy_day,
            "gestation_days": self.gestation_days,
            "expected_birth_day": self.expected_birth_day,
            "mother_name": self.mother_name,
            "father_name": self.father_name,
            "father_names": list(self.father_names),
            "mating_contact": deepcopy(self.mating_contact),
            "embryos": deepcopy(self.embryos),
            "litters": deepcopy(self.litters),
            "last_litter": deepcopy(self.last_litter),
            "litters_born": self.litters_born,
        }
