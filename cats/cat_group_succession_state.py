from dataclasses import dataclass, field

from cats.cat import Cat
from cats.cat_group_leave_state import (
    CatGroupLeaveDeniedResult,
    CatLeftGroupEvent,
)


@dataclass(slots=True, frozen=True)
class CatGroupSuccessionCandidate:
    cat: Cat
    score: float

    def __post_init__(self):
        if not isinstance(
            self.cat,
            Cat,
        ):
            raise TypeError(
                "Cat group succession candidate "
                "must contain Cat."
            )

        object.__setattr__(
            self,
            "score",
            float(self.score),
        )

    @property
    def cat_name(self):
        return self.cat.name


@dataclass(slots=True, frozen=True)
class CatGroupRoleBecameVacantEvent:
    group_id: str
    role: str
    previous_holder: str
    reason: str

    successor: str | None = field(
        default=None,
        init=False,
    )

    name: str = field(
        default="cat_group_role_became_vacant",
        init=False,
    )

    succeeded: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupRoleSucceededEvent:
    group_id: str
    role: str
    previous_holder: str
    successor: str
    successor_score: float
    reason: str

    name: str = field(
        default="cat_group_role_succeeded",
        init=False,
    )

    succeeded: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "successor_score",
            float(self.successor_score),
        )


@dataclass(slots=True, frozen=True)
class CatGroupDepartureWithSuccessionResult:
    group_id: str
    cat: str
    roles: tuple[str, ...]
    successions: tuple[
        CatGroupRoleBecameVacantEvent
        | CatGroupRoleSucceededEvent,
        ...,
    ]
    leave_result: (
        CatGroupLeaveDeniedResult
        | CatLeftGroupEvent
    )

    name: str = field(
        default="cat_group_departure_with_succession",
        init=False,
    )

    departed: bool = field(
        init=False,
    )

    def __post_init__(self):
        roles = tuple(
            str(role)
            for role in self.roles
        )

        successions = tuple(
            self.successions
        )

        for succession in successions:
            if not isinstance(
                succession,
                (
                    CatGroupRoleBecameVacantEvent,
                    CatGroupRoleSucceededEvent,
                ),
            ):
                raise TypeError(
                    "Cat group departure successions "
                    "must contain succession event objects."
                )

        if not isinstance(
            self.leave_result,
            (
                CatGroupLeaveDeniedResult,
                CatLeftGroupEvent,
            ),
        ):
            raise TypeError(
                "Cat group departure leave result "
                "must be a cat group leave result object."
            )

        object.__setattr__(
            self,
            "roles",
            roles,
        )

        object.__setattr__(
            self,
            "successions",
            successions,
        )

        object.__setattr__(
            self,
            "departed",
            bool(
                self.leave_result.left
            ),
        )
