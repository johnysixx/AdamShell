from dataclasses import dataclass, field
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Mapping

from core.entity.component_object import ComponentObject


@dataclass(frozen=True)
class CatBirthProfile:
    color: str
    fur_length: str
    pattern: str
    eye_color: str
    sex: str

    TRAITS = frozenset({
        "color",
        "fur_length",
        "pattern",
        "eye_color",
        "sex",
    })

    def with_trait(self, trait, value):
        if trait not in self.TRAITS:
            raise ValueError(
                f"Unknown cat birth trait: {trait!r}."
            )

        return replace(
            self,
            **{trait: value}
        )

    def trait_value(self, trait):
        if trait not in self.TRAITS:
            raise ValueError(
                f"Unknown cat birth trait: {trait!r}."
            )

        return getattr(self, trait)

    def to_dict(self):
        return {
            "color": self.color,
            "fur_length": self.fur_length,
            "pattern": self.pattern,
            "eye_color": self.eye_color,
            "sex": self.sex,
        }


@dataclass(frozen=True)
class CatCanonicalBirthResolution:
    matched: bool
    occurrence: int
    identity: str | None
    profile: CatBirthProfile
    special_birth_event: str | None
    woodoo_rebirth: bool = False
    woodoo_birth_number: int | None = None
    rebirth_probability: float | None = None
    forced_birth: bool = False
    forced_by: str | None = None

    def __post_init__(self):
        if not isinstance(
            self.profile,
            CatBirthProfile
        ):
            raise TypeError(
                "profile must be a CatBirthProfile object."
            )

    def to_dict(self):
        snapshot = {
            "matched": self.matched,
            "occurrence": self.occurrence,
            "identity": self.identity,
            "profile": self.profile.to_dict(),
            "special_birth_event": (
                self.special_birth_event
            ),
            "woodoo_rebirth": self.woodoo_rebirth,
        }

        if self.woodoo_birth_number is not None:
            snapshot["woodoo_birth_number"] = (
                self.woodoo_birth_number
            )

        if self.rebirth_probability is not None:
            snapshot["rebirth_probability"] = (
                self.rebirth_probability
            )

        if self.forced_birth:
            snapshot["forced_birth"] = True

        if self.forced_by is not None:
            snapshot["forced_by"] = self.forced_by

        return snapshot


@dataclass(frozen=True)
class CatGeneticsValidation:
    valid: bool
    status: str
    reason: str | None
    karyotype: str
    conflicting_trait: str | None = None
    reroll_die: str | None = None

    def to_dict(self):
        return {
            "valid": self.valid,
            "status": self.status,
            "reason": self.reason,
            "karyotype": self.karyotype,
            "conflicting_trait": self.conflicting_trait,
            "reroll_die": self.reroll_die,
        }


@dataclass(frozen=True)
class CatGeneticConflictResolution:
    attempt: int
    reason: str
    trait: str
    die: str
    previous_value: str
    new_value: str
    reroll: Mapping[str, object]

    def __post_init__(self):
        if not isinstance(self.reroll, dict):
            raise TypeError(
                "reroll must be a dict boundary payload."
            )

        object.__setattr__(
            self,
            "reroll",
            MappingProxyType(dict(self.reroll)),
        )

    def to_dict(self):
        return {
            "name": "cat_birth_genetic_conflict_resolved",
            "attempt": self.attempt,
            "reason": self.reason,
            "trait": self.trait,
            "die": self.die,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
            "reroll": dict(self.reroll),
        }


@dataclass(frozen=True)
class CatBirthGeneticsResult:
    profile: CatBirthProfile
    validation: CatGeneticsValidation
    conflict_history: tuple[CatGeneticConflictResolution, ...] = ()
    cronenbergs_created: tuple[object, ...] = ()

    def __post_init__(self):
        if not isinstance(self.profile, CatBirthProfile):
            raise TypeError(
                "profile must be a CatBirthProfile object."
            )

        if not isinstance(
            self.validation,
            CatGeneticsValidation
        ):
            raise TypeError(
                "validation must be a "
                "CatGeneticsValidation object."
            )

        if not isinstance(self.conflict_history, tuple):
            raise TypeError(
                "conflict_history must be a tuple."
            )

        if not all(
            isinstance(item, CatGeneticConflictResolution)
            for item in self.conflict_history
        ):
            raise TypeError(
                "conflict_history values must be "
                "CatGeneticConflictResolution objects."
            )

        if not isinstance(self.cronenbergs_created, tuple):
            raise TypeError(
                "cronenbergs_created must be a tuple."
            )

    @property
    def valid(self):
        return self.validation.valid

    @property
    def conflict_count(self):
        return len(self.conflict_history)

    @property
    def cronenberg_count(self):
        return len(self.cronenbergs_created)

    def to_dict(self):
        return {
            "valid": self.valid,
            "profile": self.profile.to_dict(),
            "validation": self.validation.to_dict(),
            "conflict_count": self.conflict_count,
            "conflict_history": [
                item.to_dict()
                for item in self.conflict_history
            ],
            "cronenbergs_created": list(
                self.cronenbergs_created
            ),
            "cronenberg_count": self.cronenberg_count,
        }


@dataclass(frozen=True)
class CatBirthPercentileRoll:
    die: str
    value: int
    attempt: int

    def __post_init__(self):
        if self.die != "d10_percentile":
            raise ValueError(
                "birth percentile roll must use d10_percentile."
            )

        if not isinstance(self.value, int):
            raise TypeError(
                "birth percentile value must be an integer."
            )

        if self.value not in range(0, 100, 10):
            raise ValueError(
                "birth percentile value must be one of "
                "0, 10, ..., 90."
            )

        if not isinstance(self.attempt, int) or self.attempt < 1:
            raise ValueError(
                "birth percentile attempt must be a positive integer."
            )

    @classmethod
    def from_dice_payload(cls, payload, *, attempt):
        if not isinstance(payload, dict):
            raise TypeError(
                "dice percentile payload must be a dict boundary payload."
            )

        return cls(
            die=payload["die"],
            value=int(payload["value"]),
            attempt=attempt,
        )

    @property
    def sides(self):
        return 10

    @property
    def face_value(self):
        return 10 if self.value == 0 else self.value // 10

    @property
    def raw_value(self):
        return self.face_value

    @property
    def percentile_tens(self):
        return self.value

    @property
    def is_percentile(self):
        return True

    def to_dict(self):
        return {
            "die": self.die,
            "sides": self.sides,
            "face_value": self.face_value,
            "percentile_tens": self.percentile_tens,
            "raw_value": self.raw_value,
            "value": self.value,
            "is_percentile": self.is_percentile,
            "attempt": self.attempt,
        }


@dataclass(frozen=True)
class CatBirthPercentileResult:
    final_roll: CatBirthPercentileRoll
    history: tuple[CatBirthPercentileRoll, ...]
    cronenbergs_created: tuple[object, ...] = ()

    def __post_init__(self):
        if not isinstance(
            self.final_roll,
            CatBirthPercentileRoll
        ):
            raise TypeError(
                "final_roll must be a CatBirthPercentileRoll object."
            )

        if not isinstance(self.history, tuple):
            raise TypeError(
                "history must be a tuple of percentile roll objects."
            )

        if not self.history:
            raise ValueError(
                "percentile history must contain at least one roll."
            )

        if not all(
            isinstance(item, CatBirthPercentileRoll)
            for item in self.history
        ):
            raise TypeError(
                "percentile history values must be "
                "CatBirthPercentileRoll objects."
            )

        if self.final_roll is not self.history[-1]:
            raise ValueError(
                "final_roll must be the final percentile history item."
            )

        expected_attempts = tuple(
            range(1, len(self.history) + 1)
        )
        actual_attempts = tuple(
            item.attempt
            for item in self.history
        )

        if actual_attempts != expected_attempts:
            raise ValueError(
                "percentile history attempts must be sequential."
            )

        if not isinstance(self.cronenbergs_created, tuple):
            raise TypeError(
                "cronenbergs_created must be a tuple."
            )

    @classmethod
    def single(cls, *, value):
        roll = CatBirthPercentileRoll(
            die="d10_percentile",
            value=value,
            attempt=1,
        )

        return cls(
            final_roll=roll,
            history=(roll,),
        )

    @property
    def die(self):
        return self.final_roll.die

    @property
    def value(self):
        return self.final_roll.value

    @property
    def reroll_count(self):
        return len(self.history) - 1

    @property
    def cronenberg_count(self):
        return len(self.cronenbergs_created)

    def to_dict(self):
        return {
            "final_roll": self.final_roll.to_dict(),
            "history": [
                item.to_dict()
                for item in self.history
            ],
            "reroll_count": self.reroll_count,
            "cronenbergs_created": list(
                self.cronenbergs_created
            ),
            "cronenberg_count": self.cronenberg_count,
        }


class KittenEmbryo(ComponentObject):
    pass


@dataclass(slots=True, frozen=True)
class CatKittenBirthDeniedResult:

    mother: str
    pregnancy_day: int
    gestation_days: int

    name: str = field(
        default="kitten_birth_denied",
        init=False,
    )

    reason: str = field(
        default="gestation_not_complete",
        init=False,
    )

    born: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "mother",
            str(
                self.mother
            ),
        )

        object.__setattr__(
            self,
            "pregnancy_day",
            int(
                self.pregnancy_day
            ),
        )

        object.__setattr__(
            self,
            "gestation_days",
            int(
                self.gestation_days
            ),
        )

        if (
            self.pregnancy_day
            >= self.gestation_days
        ):
            raise ValueError(
                "Birth can only be denied "
                "for incomplete gestation."
            )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "reason": self.reason,
            "mother": self.mother,
            "pregnancy_day": (
                self.pregnancy_day
            ),
            "gestation_days": (
                self.gestation_days
            ),
            "born": self.born,
        }


@dataclass(slots=True, frozen=True)
class CatKittenBirthResult:

    embryo_id: str
    kitten: str | None
    born: bool

    father: str | None = None
    genetic_status: str | None = None
    rare: bool | None = None
    reason: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "embryo_id",
            str(
                self.embryo_id
            ),
        )

        object.__setattr__(
            self,
            "born",
            bool(
                self.born
            ),
        )

        if self.kitten is not None:
            object.__setattr__(
                self,
                "kitten",
                str(
                    self.kitten
                ),
            )

        if self.father is not None:
            object.__setattr__(
                self,
                "father",
                str(
                    self.father
                ),
            )

        if self.genetic_status is not None:
            object.__setattr__(
                self,
                "genetic_status",
                str(
                    self.genetic_status
                ),
            )

        if self.rare is not None:
            object.__setattr__(
                self,
                "rare",
                bool(
                    self.rare
                ),
            )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(
                    self.reason
                ),
            )

        if self.born:
            if self.kitten is None:
                raise ValueError(
                    "Successful kitten birth "
                    "requires a kitten name."
                )

            if self.father is None:
                raise ValueError(
                    "Successful kitten birth "
                    "requires a father."
                )

            if self.genetic_status is None:
                raise ValueError(
                    "Successful kitten birth "
                    "requires genetic status."
                )

            if self.rare is None:
                raise ValueError(
                    "Successful kitten birth "
                    "requires rare state."
                )

            if self.reason is not None:
                raise ValueError(
                    "Successful kitten birth "
                    "cannot contain a failure reason."
                )

        else:
            if self.kitten is not None:
                raise ValueError(
                    "Failed kitten birth "
                    "cannot contain a kitten name."
                )

            if self.reason is None:
                raise ValueError(
                    "Failed kitten birth "
                    "requires a reason."
                )

            if (
                self.father is not None
                or self.genetic_status is not None
                or self.rare is not None
            ):
                raise ValueError(
                    "Failed kitten birth "
                    "cannot contain successful "
                    "birth details."
                )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        if not self.born:
            return {
                "embryo_id": (
                    self.embryo_id
                ),
                "kitten": None,
                "born": False,
                "reason": (
                    self.reason
                ),
            }

        return {
            "embryo_id": (
                self.embryo_id
            ),
            "kitten": self.kitten,
            "father": self.father,
            "genetic_status": (
                self.genetic_status
            ),
            "rare": self.rare,
            "born": True,
        }


@dataclass(slots=True, frozen=True)
class CatLitter:

    litter_number: int
    mother: str

    father_names: tuple[
        str,
        ...,
    ]

    embryos_present: int
    kittens_born: int

    kitten_names: tuple[
        str,
        ...,
    ]

    birth_results: tuple[
        CatKittenBirthResult,
        ...,
    ]

    pregnancy_day: int
    gestation_days: int
    birth_day: int | None

    name: str = field(
        default="cat_litter_born",
        init=False,
    )

    born: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "litter_number",
            int(
                self.litter_number
            ),
        )

        object.__setattr__(
            self,
            "mother",
            str(
                self.mother
            ),
        )

        object.__setattr__(
            self,
            "father_names",
            tuple(
                str(name)
                for name
                in self.father_names
            ),
        )

        object.__setattr__(
            self,
            "embryos_present",
            int(
                self.embryos_present
            ),
        )

        object.__setattr__(
            self,
            "kittens_born",
            int(
                self.kittens_born
            ),
        )

        object.__setattr__(
            self,
            "kitten_names",
            tuple(
                str(name)
                for name
                in self.kitten_names
            ),
        )

        object.__setattr__(
            self,
            "birth_results",
            tuple(
                self.birth_results
            ),
        )

        object.__setattr__(
            self,
            "pregnancy_day",
            int(
                self.pregnancy_day
            ),
        )

        object.__setattr__(
            self,
            "gestation_days",
            int(
                self.gestation_days
            ),
        )

        if self.birth_day is not None:
            object.__setattr__(
                self,
                "birth_day",
                int(
                    self.birth_day
                ),
            )

        if not all(
            isinstance(
                result,
                CatKittenBirthResult,
            )
            for result
            in self.birth_results
        ):
            raise TypeError(
                "Cat litter birth results "
                "must contain "
                "CatKittenBirthResult objects."
            )

        if (
            self.embryos_present
            != len(
                self.birth_results
            )
        ):
            raise ValueError(
                "Cat litter embryo count "
                "must match birth results."
            )

        if (
            self.kittens_born
            != len(
                self.kitten_names
            )
        ):
            raise ValueError(
                "Cat litter kitten count "
                "must match kitten names."
            )

        born_result_names = tuple(
            result.kitten
            for result
            in self.birth_results
            if result.born
        )

        if (
            born_result_names
            != self.kitten_names
        ):
            raise ValueError(
                "Cat litter kitten names "
                "must match successful "
                "birth results."
            )

    @property
    def multiple_sires(self):
        return (
            len(
                self.father_names
            )
            > 1
        )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "litter_number": (
                self.litter_number
            ),
            "mother": self.mother,
            "father_names": list(
                self.father_names
            ),
            "multiple_sires": (
                self.multiple_sires
            ),
            "embryos_present": (
                self.embryos_present
            ),
            "kittens_born": (
                self.kittens_born
            ),
            "kitten_names": list(
                self.kitten_names
            ),
            "birth_results": [
                result.to_dict()
                for result
                in self.birth_results
            ],
            "pregnancy_day": (
                self.pregnancy_day
            ),
            "gestation_days": (
                self.gestation_days
            ),
            "birth_day": self.birth_day,
            "born": self.born,
        }
