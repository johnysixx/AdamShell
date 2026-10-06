from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupCultureInheritedEvent:
    parent_group: str
    child_group: str
    retention: float
    inherited_traits: tuple[str, ...]
    inherited_traditions: tuple[str, ...]
    inherited_preferences: tuple[str, ...]

    name: str = field(
        default="cat_group_culture_inherited",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "retention",
            float(
                self.retention
            ),
        )

        for name in (
            "inherited_traits",
            "inherited_traditions",
            "inherited_preferences",
        ):
            object.__setattr__(
                self,
                name,
                tuple(
                    getattr(
                        self,
                        name,
                    )
                ),
            )


@dataclass(slots=True, frozen=True)
class CatGroupCultureDivergenceResult:
    parent_group: str
    child_group: str
    divergence: float

    def __post_init__(self):
        object.__setattr__(
            self,
            "divergence",
            float(
                self.divergence
            ),
        )
