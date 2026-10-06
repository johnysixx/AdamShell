from dataclasses import dataclass, field

from cats.cat_group_diplomacy_state import (
    CatGroupMutualRelationResult,
)


@dataclass(slots=True, frozen=True)
class CatGroupAllianceDeniedResult:
    first_group: str
    second_group: str
    reason: str
    relation: CatGroupMutualRelationResult | None = None

    name: str = field(
        default="cat_group_alliance_denied",
        init=False,
    )

    formed: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if (
            self.relation is not None
            and not isinstance(
                self.relation,
                CatGroupMutualRelationResult,
            )
        ):
            raise TypeError(
                "Cat group alliance relation must be "
                "CatGroupMutualRelationResult."
            )


@dataclass(slots=True, frozen=True)
class CatGroupAlliancePreservedResult:
    first_group: str
    second_group: str

    name: str = field(
        default="cat_group_alliance_preserved",
        init=False,
    )

    formed: bool = field(
        default=True,
        init=False,
    )

    existing: bool = field(
        default=True,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupAllianceFormedEvent:
    first_group: str
    second_group: str
    relation: CatGroupMutualRelationResult

    name: str = field(
        default="cat_group_alliance_formed",
        init=False,
    )

    formed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.relation,
            CatGroupMutualRelationResult,
        ):
            raise TypeError(
                "Cat group alliance relation must be "
                "CatGroupMutualRelationResult."
            )
