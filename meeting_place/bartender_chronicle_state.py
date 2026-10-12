from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType


@dataclass(slots=True, frozen=True)
class BartenderObservedEjectionEntry:
    subject: str | None
    observed_reason: str | None

    kind: str = field(
        default="ejection",
        init=False,
    )

    observed_outcome: str = field(
        default="ejected",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "subject",
            (
                None
                if self.subject is None
                else str(self.subject)
            ),
        )

        object.__setattr__(
            self,
            "observed_reason",
            (
                None
                if self.observed_reason is None
                else str(
                    self.observed_reason
                )
            ),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "subject": self.subject,
            "observed_reason":
                self.observed_reason,
            "observed_outcome":
                self.observed_outcome,
        }


@dataclass(slots=True, frozen=True)
class BartenderObservedEventEntry:
    observed_event: object

    kind: str = field(
        default="ordinary",
        init=False,
    )

    def to_dict(self):
        observed_event = (
            self.observed_event
        )

        serializer = getattr(
            observed_event,
            "to_dict",
            None,
        )

        if callable(
            serializer
        ):
            observed_event = (
                serializer()
            )

        return {
            "kind": self.kind,
            "observed_event":
                observed_event,
        }


@dataclass(slots=True, frozen=True)
class BartenderLearnedCocktailEntry:
    drink: str
    teacher: str
    ingredients: tuple[str, ...]

    kind: str = field(
        default="learned_cocktail",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )

        object.__setattr__(
            self,
            "ingredients",
            tuple(
                str(ingredient)
                for ingredient
                in self.ingredients
            ),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "drink": self.drink,
            "teacher": self.teacher,
            "ingredients": list(
                self.ingredients
            ),
        }


@dataclass(slots=True, frozen=True)
class BartenderLearnedGuestDrinkEntry:
    drink: str
    teacher: str
    ingredients: tuple[str, ...]
    effects: object = field(
        default_factory=dict
    )
    price_basis: str | None = None

    kind: str = field(
        default="learned_cocktail",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )

        object.__setattr__(
            self,
            "ingredients",
            tuple(
                str(ingredient)
                for ingredient
                in self.ingredients
            ),
        )

        object.__setattr__(
            self,
            "effects",
            MappingProxyType(
                deepcopy(
                    dict(
                        self.effects or {}
                    )
                )
            ),
        )

        object.__setattr__(
            self,
            "price_basis",
            (
                None
                if self.price_basis is None
                else str(self.price_basis)
            ),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "drink": self.drink,
            "teacher": self.teacher,
            "ingredients": list(
                self.ingredients
            ),
            "effects": deepcopy(
                dict(self.effects)
            ),
            "price_basis":
                self.price_basis,
        }


@dataclass(slots=True, frozen=True)
class BartenderCreatedCocktailEntry:
    drink: str

    kind: str = field(
        default="created_cocktail",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class BartenderNewDrinkEntry:
    drink: str
    source: str

    kind: str = field(
        default="new_drink",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

        object.__setattr__(
            self,
            "source",
            str(self.source),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "drink": self.drink,
            "source": self.source,
        }


@dataclass(slots=True, frozen=True)
class BartenderInterestingGuestEntry:
    guest: str
    reason: str

    kind: str = field(
        default="interesting_guest",
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
            "reason",
            str(self.reason),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "guest": self.guest,
            "reason": self.reason,
        }


@dataclass(slots=True, frozen=True)
class BartenderCocktailDecisionEntry:
    drink: str
    votes_for: int
    votes_against: int
    approved: bool

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

        object.__setattr__(
            self,
            "votes_for",
            int(self.votes_for),
        )

        object.__setattr__(
            self,
            "votes_against",
            int(self.votes_against),
        )

        object.__setattr__(
            self,
            "approved",
            bool(self.approved),
        )

    @property
    def kind(self):
        if self.approved:
            return "cocktail_approved"

        return "cocktail_rejected"

    def to_dict(self):
        return {
            "kind": self.kind,
            "drink": self.drink,
            "votes_for":
                self.votes_for,
            "votes_against":
                self.votes_against,
        }


@dataclass(slots=True, frozen=True)
class BartenderNewMenuDrinkEntry:
    drink: str

    kind: str = field(
        default="new_menu_drink",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "drink": self.drink,
        }


@dataclass(slots=True, frozen=True)
class BartenderDrinkPromotedEntry:
    drink: str

    kind: str = field(
        default="drink_promoted",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "drink",
            str(self.drink),
        )

    def to_dict(self):
        return {
            "kind": self.kind,
            "drink": self.drink,
        }


BARTENDER_CHRONICLE_MEMORY_TYPES = (
    BartenderLearnedCocktailEntry,
    BartenderLearnedGuestDrinkEntry,
    BartenderCreatedCocktailEntry,
    BartenderNewDrinkEntry,
    BartenderInterestingGuestEntry,
    BartenderCocktailDecisionEntry,
    BartenderNewMenuDrinkEntry,
    BartenderDrinkPromotedEntry,
)


BARTENDER_SHIFT_EVENT_TYPES = (
    BartenderObservedEjectionEntry,
    BartenderObservedEventEntry,
    *BARTENDER_CHRONICLE_MEMORY_TYPES,
)


@dataclass(slots=True, frozen=True)
class BartenderShiftChronicle:
    observer: str
    bar_day: int | None
    shift_start_tick: int | None
    shift_end_tick: int | None
    events: tuple

    type: str = field(
        default="bartender_shift_chronicle",
        init=False,
    )

    perspective: str = field(
        default="subjective",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "observer",
            str(self.observer),
        )

        for field_name in (
            "bar_day",
            "shift_start_tick",
            "shift_end_tick",
        ):
            value = getattr(
                self,
                field_name,
            )

            object.__setattr__(
                self,
                field_name,
                (
                    None
                    if value is None
                    else int(value)
                ),
            )

        events = tuple(
            self.events
        )

        for event in events:
            if not isinstance(
                event,
                BARTENDER_SHIFT_EVENT_TYPES,
            ):
                raise TypeError(
                    "Bartender shift chronicle "
                    "requires typed chronicle "
                    "event objects."
                )

        object.__setattr__(
            self,
            "events",
            events,
        )

    def to_dict(self):
        return {
            "type": self.type,
            "observer": self.observer,
            "perspective":
                self.perspective,
            "bar_day": self.bar_day,
            "shift_start_tick":
                self.shift_start_tick,
            "shift_end_tick":
                self.shift_end_tick,
            "events": [
                event.to_dict()
                for event
                in self.events
            ],
        }
