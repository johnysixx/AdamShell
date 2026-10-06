from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatRitualMutationDeniedResult:
    reason: str

    name: str = field(
        default="cat_ritual_mutation_denied",
        init=False,
    )

    mutated: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupRitualMutatedEvent:
    group_id: str
    parent_ritual: str
    new_ritual: str
    lineage_root: str
    generation: int
    reason: str

    name: str = field(
        default="cat_group_ritual_mutated",
        init=False,
    )

    mutated: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "generation",
            int(
                self.generation
            ),
        )
