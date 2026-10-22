from dataclasses import dataclass, field

from cats.cat_social_objects import (
    CatTerritoryClaim,
)
from core.entity.domain_object import (
    DomainObject,
)


class CatGroupTerritories(
    DomainObject
):

    def __init__(
        self,
    ):
        self._records = []

    @property
    def is_empty(
        self,
    ):
        return not self._records

    @property
    def count(
        self,
    ):
        return len(
            self._records
        )

    def store(
        self,
        state,
    ):
        if not isinstance(
            state,
            CatGroupTerritoryState,
        ):
            raise TypeError(
                "Cat group territory registry requires "
                "CatGroupTerritoryState."
            )

        layer = getattr(
            state,
            "layer",
            None,
        )

        if (
            not isinstance(
                layer,
                str,
            )
            or not layer
        ):
            raise ValueError(
                "Stored cat group territory "
                "requires layer."
            )

        for index, current in enumerate(
            self.records()
        ):
            if (
                current.layer
                == state.layer
                and current.location
                == state.location
            ):
                self._records[
                    index
                ] = state

                return state

        self._records.append(
            state
        )

        return state

    def record(
        self,
        layer,
        location,
    ):
        layer = str(
            layer
        )

        for state in self.records():
            if (
                state.layer
                == layer
                and state.location
                == location
            ):
                return state

        return None

    def has(
        self,
        layer,
        location,
    ):
        return (
            self.record(
                layer,
                location,
            )
            is not None
        )

    def records(
        self,
    ):
        for state in self._records:
            if not isinstance(
                state,
                CatGroupTerritoryState,
            ):
                raise TypeError(
                    "Cat group territory registry "
                    "contains invalid runtime state."
                )

        return tuple(
            self._records
        )

    def identifiers(
        self,
    ):
        return tuple(
            f"{state.layer}::{state.location}"
            for state in self.records()
        )


@dataclass(slots=True)
class CatGroupTerritoryState:
    layer: str | None = None
    location: object = None
    strength: float = 0.0
    members: list = field(
        default_factory=list
    )

    def record_claim(
        self,
        layer,
        location,
        strength,
        members,
    ):
        self.layer = layer
        self.location = location
        self.strength = float(
            strength
        )
        self.members = list(
            members
        )

        return self

@dataclass(slots=True, frozen=True)
class CatGroupTerritoryClaimedEvent:
    group_id: str
    territory: str
    member_count: int

    name: str = field(
        default="cat_group_territory_claimed",
        init=False,
    )

    claimed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "member_count",
            int(
                self.member_count
            ),
        )


@dataclass(slots=True, frozen=True)
class CatGroupTerritoryClaimedResult:
    group_id: str
    territory: str
    member_count: int
    claims: tuple[CatTerritoryClaim, ...]

    name: str = field(
        default="cat_group_territory_claimed",
        init=False,
    )

    claimed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        claims = tuple(
            self.claims
        )

        for claim in claims:
            if not isinstance(
                claim,
                CatTerritoryClaim,
            ):
                raise TypeError(
                    "Cat group territory claims "
                    "must contain CatTerritoryClaim objects."
                )

        object.__setattr__(
            self,
            "claims",
            claims,
        )

        object.__setattr__(
            self,
            "member_count",
            int(
                self.member_count
            ),
        )
