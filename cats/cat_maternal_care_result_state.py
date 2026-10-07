from dataclasses import dataclass, field

from cats.maternal_care_phase import (
    MaternalCarePhase,
)


@dataclass(slots=True, frozen=True)
class CatMaternalCareAssessment:
    mother: str
    kitten: str
    biological_child: bool
    phase: MaternalCarePhase
    nursing: bool
    cleaning: bool
    warming: bool
    protection: bool
    retrieval: bool
    active: bool

    name: str = field(
        default="cat_maternal_care_assessment",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.phase,
            MaternalCarePhase,
        ):
            raise TypeError(
                "Maternal care assessment phase "
                "must use MaternalCarePhase."
            )

        for attribute in (
            "biological_child",
            "nursing",
            "cleaning",
            "warming",
            "protection",
            "retrieval",
            "active",
        ):
            object.__setattr__(
                self,
                attribute,
                bool(
                    getattr(
                        self,
                        attribute,
                    )
                ),
            )


@dataclass(slots=True, frozen=True)
class CatMaternalCareDeniedResult:
    mother: str
    kitten: str
    reason: str

    name: str = field(
        default="maternal_care_denied",
        init=False,
    )

    provided: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatMaternalCareEvent:
    mother: str
    kitten: str
    age_days: int
    day: int | None
    phase: MaternalCarePhase
    actions: tuple[str, ...]

    name: str = field(
        default="cat_maternal_care",
        init=False,
    )

    provided: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.phase,
            MaternalCarePhase,
        ):
            raise TypeError(
                "Maternal care event phase "
                "must use MaternalCarePhase."
            )

        object.__setattr__(
            self,
            "age_days",
            int(self.age_days),
        )

        if self.day is not None:
            object.__setattr__(
                self,
                "day",
                int(self.day),
            )

        object.__setattr__(
            self,
            "actions",
            tuple(self.actions),
        )


@dataclass(slots=True, frozen=True)
class CatMaternalProtectionDeniedResult:
    mother: str
    kitten: str
    reason: str

    name: str = field(
        default="maternal_protection_denied",
        init=False,
    )

    protected: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatMotherProtectedKittenEvent:
    mother: str
    kitten: str
    threat: str | None
    day: int | None

    name: str = field(
        default="mother_protected_kitten",
        init=False,
    )

    protected: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if self.day is not None:
            object.__setattr__(
                self,
                "day",
                int(self.day),
            )



@dataclass(slots=True, frozen=True)
class CatFosterMaternalCareDeniedResult:
    foster_mother: str
    kitten: str
    reason: str

    name: str = field(
        default="foster_maternal_care_denied",
        init=False,
    )

    provided: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatFosterMaternalCareEvent:
    foster_mother: str
    kitten: str
    age_days: int
    day: int | None
    phase: MaternalCarePhase
    actions: tuple[str, ...]

    name: str = field(
        default="cat_foster_maternal_care",
        init=False,
    )

    provided: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.phase,
            MaternalCarePhase,
        ):
            raise TypeError(
                "Foster maternal care event phase "
                "must use MaternalCarePhase."
            )

        object.__setattr__(
            self,
            "age_days",
            int(self.age_days),
        )

        if self.day is not None:
            object.__setattr__(
                self,
                "day",
                int(self.day),
            )

        object.__setattr__(
            self,
            "actions",
            tuple(self.actions),
        )
