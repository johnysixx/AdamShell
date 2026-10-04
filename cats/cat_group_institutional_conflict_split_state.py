from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatInstitutionSplitDeniedResult:
    reason: str

    name: str = field(
        default="cat_institution_split_denied",
        init=False,
    )

    split: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatInstitutionalSplitResult:
    group_id: str
    conflict_id: str
    institutions: tuple[str, ...]

    name: str = field(
        default="cat_institutional_split",
        init=False,
    )

    split: bool = field(
        default=True,
        init=False,
    )
