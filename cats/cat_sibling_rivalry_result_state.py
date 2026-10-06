from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatSiblingRivalryDeniedResult:
    first: str
    second: str
    reason: str

    name: str = field(
        default="sibling_rivalry_denied",
        init=False,
    )

    competed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatSiblingRivalryEvent:
    first: str
    second: str
    relation: str
    resource: str
    intensity: float
    outcome: str
    bonded: bool

    name: str = field(
        default="cat_sibling_rivalry",
        init=False,
    )

    competed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "intensity",
            float(self.intensity),
        )

        object.__setattr__(
            self,
            "bonded",
            bool(self.bonded),
        )


@dataclass(slots=True, frozen=True)
class CatSiblingReconciliationDeniedResult:
    first: str
    second: str
    reason: str

    name: str = field(
        default="sibling_reconciliation_denied",
        init=False,
    )

    reconciled: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatSiblingsReconciledEvent:
    first: str
    second: str

    name: str = field(
        default="cat_siblings_reconciled",
        init=False,
    )

    reconciled: bool = field(
        default=True,
        init=False,
    )
