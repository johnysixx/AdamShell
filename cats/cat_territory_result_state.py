from dataclasses import (
    dataclass,
    field,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatTerritoryClaimedEvent:

    cat: str
    territory: str
    layer: str | None
    location: str | None
    strength: float
    scent_marks: int

    name: str = field(
        default="cat_claimed_territory",
        init=False,
    )

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "strength",
            float(
                self.strength
            ),
        )

        object.__setattr__(
            self,
            "scent_marks",
            int(
                self.scent_marks
            ),
        )


@dataclass(
    slots=True,
    frozen=True,
)
class CatTerritoryScentMarkedEvent:

    cat: str
    territory: str
    strength: float
    scent_marks: int

    name: str = field(
        default="cat_scent_marked_territory",
        init=False,
    )

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "strength",
            float(
                self.strength
            ),
        )

        object.__setattr__(
            self,
            "scent_marks",
            int(
                self.scent_marks
            ),
        )
