from dataclasses import (
    dataclass,
    field,
)


@dataclass(
    slots=True,
    frozen=True,
)
class CatBondEvaluation:

    cat: str
    other_cat: str

    eligible: bool
    strength: float

    familiarity: float
    trust: float
    affiliation: float
    shared_scent: float
    tension: float

    friendly_memories: int
    hostile_memories: int

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "eligible",
            bool(
                self.eligible
            ),
        )

        for name in (
            "strength",
            "familiarity",
            "trust",
            "affiliation",
            "shared_scent",
            "tension",
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
            "friendly_memories",
            int(
                self.friendly_memories
            ),
        )

        object.__setattr__(
            self,
            "hostile_memories",
            int(
                self.hostile_memories
            ),
        )


@dataclass(
    slots=True,
    frozen=True,
)
class CatBondNotFormedResult:

    cat: str
    other_cat: str
    reason: str

    cat_evaluation: CatBondEvaluation
    other_cat_evaluation: CatBondEvaluation

    name: str = field(
        default="cat_bond_not_formed",
        init=False,
    )

    formed: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.cat_evaluation,
            CatBondEvaluation,
        ):
            raise TypeError(
                "Cat bond evaluation must be "
                "CatBondEvaluation."
            )

        if not isinstance(
            self.other_cat_evaluation,
            CatBondEvaluation,
        ):
            raise TypeError(
                "Other cat bond evaluation must be "
                "CatBondEvaluation."
            )


@dataclass(
    slots=True,
    frozen=True,
)
class CatBondFormedEvent:

    cat: str
    other_cat: str
    strength: float
    behaviors: tuple[str, ...]

    name: str = field(
        default="cat_bond_formed",
        init=False,
    )

    formed: bool = field(
        default=True,
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
            "behaviors",
            tuple(
                self.behaviors
            ),
        )


@dataclass(
    slots=True,
    frozen=True,
)
class CatBondPreservedEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_bond_preserved",
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


@dataclass(
    slots=True,
    frozen=True,
)
class CatBondActionDeniedResult:

    cat: str
    other_cat: str
    action: str
    reason: str

    name: str = field(
        default="cat_bond_action_denied",
        init=False,
    )

    performed: bool = field(
        default=False,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatsMutuallyGroomedEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cats_mutually_groomed",
        init=False,
    )

    bonded: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class BondedCatsSleptTogetherEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="bonded_cats_slept_together",
        init=False,
    )

    bonded: bool = field(
        default=True,
        init=False,
    )

    performed: bool = field(
        default=True,
        init=False,
    )


@dataclass(
    slots=True,
    frozen=True,
)
class CatFollowingBondedCatEvent:

    cat: str
    other_cat: str

    name: str = field(
        default="cat_following_bonded_cat",
        init=False,
    )

    bonded: bool = field(
        default=True,
        init=False,
    )

    performed: bool = field(
        default=True,
        init=False,
    )
