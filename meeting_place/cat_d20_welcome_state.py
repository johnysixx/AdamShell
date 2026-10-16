from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatD20WelcomeEventState:
    cat: str
    milk_served: bool
    box: str
    box_location: str
    cat_entered_box: bool
    tick: int

    name: str = field(
        default="cat_d20_welcomed_at_bar",
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
            "milk_served",
            bool(self.milk_served),
        )

        object.__setattr__(
            self,
            "box",
            str(self.box),
        )

        object.__setattr__(
            self,
            "box_location",
            str(self.box_location),
        )

        object.__setattr__(
            self,
            "cat_entered_box",
            bool(self.cat_entered_box),
        )

        object.__setattr__(
            self,
            "tick",
            int(self.tick),
        )


@dataclass(slots=True, frozen=True)
class CatD20WelcomeResultState:
    cat: object
    box: object | None
    created: bool
    entity: object | None = None
    event: CatD20WelcomeEventState | None = None

    name: str = field(
        init=False,
    )

    def __post_init__(self):
        created = bool(
            self.created
        )

        object.__setattr__(
            self,
            "created",
            created,
        )

        if created:
            if not isinstance(
                self.event,
                CatD20WelcomeEventState,
            ):
                raise TypeError(
                    "Completed CatD20 welcome "
                    "requires "
                    "CatD20WelcomeEventState."
                )

            if self.box is None:
                raise ValueError(
                    "Completed CatD20 welcome "
                    "requires a box."
                )

            object.__setattr__(
                self,
                "name",
                "cat_d20_arrival_completed",
            )

        else:
            if self.event is not None:
                raise ValueError(
                    "Already-present CatD20 "
                    "cannot have a new welcome event."
                )

            object.__setattr__(
                self,
                "name",
                "cat_d20_already_present",
            )
