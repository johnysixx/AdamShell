from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class BartenderShiftStartedEvent:
    bar_day: int
    shift_start_tick: int

    name: str = field(
        default="bartender_shift_started",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "bar_day",
            int(self.bar_day),
        )

        object.__setattr__(
            self,
            "shift_start_tick",
            int(self.shift_start_tick),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "bar_day": self.bar_day,
            "shift_start_tick":
                self.shift_start_tick,
        }


@dataclass(slots=True, frozen=True)
class BartenderShiftAlreadyActiveResult:
    bar_day: int
    shift_start_tick: int

    name: str = field(
        default="bartender_shift_already_active",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "bar_day",
            int(self.bar_day),
        )

        object.__setattr__(
            self,
            "shift_start_tick",
            int(self.shift_start_tick),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "bar_day": self.bar_day,
            "shift_start_tick":
                self.shift_start_tick,
        }


@dataclass(slots=True, frozen=True)
class BartenderRefusedBetEvent:
    guest: str

    name: str = field(
        default="bartender_refused_bet",
        init=False,
    )

    accepted: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "guest",
            str(self.guest),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "accepted": self.accepted,
        }


@dataclass(slots=True, frozen=True)
class BartenderLearnedRequestedDrinkEvent:
    guest: str
    drink: str

    name: str = field(
        default="bartender_learned_requested_drink",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "guest",
            str(self.guest),
        )

        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class BartenderLeftForLemonEvent:
    guest: str

    name: str = field(
        default="bartender_left_for_lemon",
        init=False,
    )

    destination: str = field(
        default="bar_yard",
        init=False,
    )

    reason: str = field(
        default="fetch_lemon",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "guest",
            str(self.guest),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "destination":
                self.destination,
            "reason": self.reason,
        }


@dataclass(slots=True, frozen=True)
class BartenderReturnedWithLemonEvent:
    guest: str

    name: str = field(
        default="bartender_returned_with_lemon",
        init=False,
    )

    source: str = field(
        default="bar_yard",
        init=False,
    )

    ingredient: str = field(
        default="lemon",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "guest",
            str(self.guest),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "source": self.source,
            "ingredient":
                self.ingredient,
        }


BARTENDER_EVENT_TYPES = (
    BartenderShiftStartedEvent,
    BartenderRefusedBetEvent,
    BartenderLearnedRequestedDrinkEvent,
    BartenderLeftForLemonEvent,
    BartenderReturnedWithLemonEvent,
)
