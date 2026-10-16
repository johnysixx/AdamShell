from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatD20ProfilePreparationFailedResult:
    reason: str

    name: str = field(
        default="cat_d20_pazuzu_profile_failed",
        init=False,
    )

    prepared: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )
