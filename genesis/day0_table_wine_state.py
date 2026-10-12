from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class LilithTakesFirstTableSipEvent:
    name: str = field(
        default="lilith_takes_first_sip_of_lilith",
        init=False,
    )
    guest: str = field(
        default="lilith",
        init=False,
    )
    drink: str = field(
        default="lilith",
        init=False,
    )
    effects_applied: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "effects_applied":
                self.effects_applied,
        }


@dataclass(slots=True, frozen=True)
class SerpentFinishesWineAtTableEvent:
    name: str = field(
        default="serpent_finishes_wine_at_table",
        init=False,
    )
    guest: str = field(
        default="serpent",
        init=False,
    )
    drink: str = field(
        default="wine",
        init=False,
    )
    finished: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "finished": self.finished,
        }


@dataclass(slots=True, frozen=True)
class FirstTableDrinksResult:
    lilith: LilithTakesFirstTableSipEvent
    serpent: SerpentFinishesWineAtTableEvent

    def __post_init__(self):
        if not isinstance(
            self.lilith,
            LilithTakesFirstTableSipEvent,
        ):
            raise TypeError(
                "First table drinks result requires "
                "LilithTakesFirstTableSipEvent."
            )

        if not isinstance(
            self.serpent,
            SerpentFinishesWineAtTableEvent,
        ):
            raise TypeError(
                "First table drinks result requires "
                "SerpentFinishesWineAtTableEvent."
            )

    def to_dict(self):
        return {
            "lilith":
                self.lilith.to_dict(),
            "serpent":
                self.serpent.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class FirstGoodWineObservationEvent:
    name: str = field(
        default="first_good_wine_observation",
        init=False,
    )
    subject: str = field(
        default="wine",
        init=False,
    )
    wine_tastes_like_water: bool = field(
        default=True,
        init=False,
    )
    desired_flavor: str = field(
        default="fuller",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "subject": self.subject,
            "wine_tastes_like_water":
                self.wine_tastes_like_water,
            "desired_flavor":
                self.desired_flavor,
        }


@dataclass(slots=True, frozen=True)
class GodArrivesDuringWineDiscussionEvent:
    name: str = field(
        default="god_arrives_during_wine_discussion",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    source: str = field(
        default="library",
        init=False,
    )
    destination: str = field(
        default="bar",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "from": self.source,
            "to": self.destination,
        }


@dataclass(slots=True, frozen=True)
class GodLooksAroundBarEvent:
    name: str = field(
        default="god_looks_around_bar",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    activity: str = field(
        default="looking_around",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "activity": self.activity,
        }


@dataclass(slots=True, frozen=True)
class GodBrowsesDrinkMenuEvent:
    available_drinks: tuple[str, ...]

    name: str = field(
        default="god_browses_drink_menu",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "available_drinks",
            tuple(
                str(drink)
                for drink
                in self.available_drinks
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "available_drinks": list(
                self.available_drinks
            ),
        }


@dataclass(slots=True, frozen=True)
class SerpentLilithContinueWineDiscussionEvent:
    participants: tuple[str, ...] = (
        "serpent",
        "lilith",
    )

    name: str = field(
        default=(
            "serpent_and_lilith_"
            "continue_wine_discussion"
        ),
        init=False,
    )
    subject: str = field(
        default="wine",
        init=False,
    )
    previous_idea: str = field(
        default="flavor_should_be_fuller",
        init=False,
    )
    new_idea: str | None = field(
        default=None,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "participants",
            tuple(
                str(participant)
                for participant
                in self.participants
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "participants": list(
                self.participants
            ),
            "subject": self.subject,
            "previous_idea":
                self.previous_idea,
            "new_idea":
                self.new_idea,
        }
