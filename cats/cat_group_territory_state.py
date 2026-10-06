from dataclasses import dataclass, field

from cats.cat_social_objects import (
    CatTerritoryClaim,
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
