from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupInfluenceRankEntry:
    cat: str
    influence: float

    def __post_init__(self):
        object.__setattr__(
            self,
            "influence",
            float(self.influence),
        )


@dataclass(slots=True, frozen=True)
class CatGroupInfluenceRankingResult:
    group_id: str
    ranking: tuple[
        CatGroupInfluenceRankEntry,
        ...
    ]

    ranked: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        ranking = tuple(
            self.ranking
        )

        for entry in ranking:
            if not isinstance(
                entry,
                CatGroupInfluenceRankEntry,
            ):
                raise TypeError(
                    "Cat group influence ranking "
                    "must contain "
                    "CatGroupInfluenceRankEntry "
                    "objects."
                )

        object.__setattr__(
            self,
            "ranking",
            ranking,
        )


@dataclass(slots=True, frozen=True)
class CatGroupInfluenceRankedEvent:
    group_id: str
    ranking: tuple[
        CatGroupInfluenceRankEntry,
        ...
    ]

    name: str = field(
        default="cat_group_influence_ranked",
        init=False,
    )

    def __post_init__(self):
        ranking = tuple(
            self.ranking
        )

        for entry in ranking:
            if not isinstance(
                entry,
                CatGroupInfluenceRankEntry,
            ):
                raise TypeError(
                    "Cat group influence event "
                    "must contain "
                    "CatGroupInfluenceRankEntry "
                    "objects."
                )

        object.__setattr__(
            self,
            "ranking",
            ranking,
        )
