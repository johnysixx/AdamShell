from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatOverpopulationActivationDeniedResult:

    reason: str
    cat: str | None = None

    name: str = field(
        default="cat_overpopulation_activation_denied",
        init=False,
    )

    activated: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

        if self.cat is not None:
            object.__setattr__(
                self,
                "cat",
                str(self.cat),
            )


@dataclass(slots=True, frozen=True)
class CatOverpopulationActivatedEvent:

    cat: str
    suggested_intent: str
    cronenbergs_eaten: int
    hunt_quota: int

    name: str = field(
        default="cat_activated_for_cronenberg_overpopulation",
        init=False,
    )

    cat_access_unchanged: bool = field(
        default=True,
        init=False,
    )

    activated: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "suggested_intent",
            str(self.suggested_intent),
        )

        object.__setattr__(
            self,
            "cronenbergs_eaten",
            int(self.cronenbergs_eaten),
        )

        object.__setattr__(
            self,
            "hunt_quota",
            int(self.hunt_quota),
        )
