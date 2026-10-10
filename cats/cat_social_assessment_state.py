from dataclasses import dataclass


@dataclass(
    slots=True,
    frozen=True,
)
class CatTerritoryContext:

    owns_here: bool
    intrusion: bool
    accepted: bool
    claim_strength: float
    territory: str | None

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "owns_here",
            bool(
                self.owns_here
            ),
        )

        object.__setattr__(
            self,
            "intrusion",
            bool(
                self.intrusion
            ),
        )

        object.__setattr__(
            self,
            "accepted",
            bool(
                self.accepted
            ),
        )

        object.__setattr__(
            self,
            "claim_strength",
            float(
                self.claim_strength
            ),
        )


@dataclass(
    slots=True,
    frozen=True,
)
class CatFamilySocialBias:

    friendly: float
    territory_multiplier: float
    protected_from_territorial_hostility: bool

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "friendly",
            float(
                self.friendly
            ),
        )

        object.__setattr__(
            self,
            "territory_multiplier",
            float(
                self.territory_multiplier
            ),
        )

        object.__setattr__(
            self,
            "protected_from_territorial_hostility",
            bool(
                self
                .protected_from_territorial_hostility
            ),
        )


@dataclass(
    slots=True,
    frozen=True,
)
class CatSocialAssessment:

    cat: str
    other_cat: str
    known: bool
    attitude: str

    friendly_score: float

    familiarity: float
    trust: float
    affiliation: float
    tension: float

    empathy: float
    sociability: float
    courage: float
    aggression: float

    positive_social_memories: int
    negative_social_memories: int

    memory_bias: float
    last_social_outcome: object

    territory: CatTerritoryContext
    territorial_pressure: float

    family_relation: str | None
    family_bias: CatFamilySocialBias

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.territory,
            CatTerritoryContext,
        ):
            raise TypeError(
                "Social assessment territory "
                "must be CatTerritoryContext."
            )

        if not isinstance(
            self.family_bias,
            CatFamilySocialBias,
        ):
            raise TypeError(
                "Social assessment family bias "
                "must be CatFamilySocialBias."
            )

        object.__setattr__(
            self,
            "known",
            bool(
                self.known
            ),
        )

        for name in (
            "friendly_score",
            "familiarity",
            "trust",
            "affiliation",
            "tension",
            "empathy",
            "sociability",
            "courage",
            "aggression",
            "memory_bias",
            "territorial_pressure",
        ):
            object.__setattr__(
                self,
                name,
                float(
                    getattr(
                        self,
                        name,
                    )
                ),
            )

        object.__setattr__(
            self,
            "positive_social_memories",
            int(
                self
                .positive_social_memories
            ),
        )

        object.__setattr__(
            self,
            "negative_social_memories",
            int(
                self
                .negative_social_memories
            ),
        )
