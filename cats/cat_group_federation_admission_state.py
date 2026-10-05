from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatFederationAdmissionSkippedResult:
    reason: str

    name: str = field(
        default="cat_federation_admission_skipped",
        init=False,
    )

    admitted: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatFederationAdmissionDeniedResult:
    reason: str
    score: float

    name: str = field(
        default="cat_federation_admission_denied",
        init=False,
    )

    admitted: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupJoinedFederationEvent:
    federation_id: str
    group_id: str

    name: str = field(
        default="cat_group_joined_federation",
        init=False,
    )

    admitted: bool = field(
        default=True,
        init=False,
    )
