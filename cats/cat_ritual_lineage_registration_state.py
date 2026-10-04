from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatRitualLineageRegistrationDeniedResult:
    reason: str

    name: str = field(
        default="cat_ritual_lineage_denied",
        init=False,
    )

    registered: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatRitualLineageRegisteredResult:
    group_id: str
    ritual: str

    name: str = field(
        default="cat_ritual_lineage_registered",
        init=False,
    )

    registered: bool = field(
        default=True,
        init=False,
    )
