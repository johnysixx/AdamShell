from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrinkWager,
)


@dataclass(slots=True, frozen=True)
class FirstBarDrinkReactionState:
    wine: str = "dislikes"
    beer: str = "dislikes"
    mead: str = "dislikes"

    def to_dict(self):
        return {
            "wine": self.wine,
            "beer": self.beer,
            "mead": self.mead,
        }


@dataclass(slots=True, frozen=True)
class InitialBarDrinkWagerSnapshot:
    participants: tuple[str, ...]
    eligible_drinks: tuple[str, ...]
    make_something_better: bool
    existing_better_example: bool
    winner_stake: str
    loser_stake: str
    proposed_by: str
    accepted_by: str | None
    accepted: bool
    resolved: bool
    winner: str | None
    loser: str | None

    @classmethod
    def from_wager(
        cls,
        wager,
    ):
        if not isinstance(
            wager,
            BarDrinkWager,
        ):
            raise TypeError(
                "Initial wager snapshot requires "
                "a BarDrinkWager object."
            )

        return cls(
            participants=tuple(
                wager.participants
            ),
            eligible_drinks=tuple(
                wager
                .challenge
                .eligible_drinks
            ),
            make_something_better=(
                wager
                .challenge
                .make_something_better
            ),
            existing_better_example=(
                wager
                .challenge
                .existing_better_example
            ),
            winner_stake=(
                wager.stakes.winner
            ),
            loser_stake=(
                wager.stakes.loser
            ),
            proposed_by=(
                wager.proposed_by
            ),
            accepted_by=(
                wager.accepted_by
            ),
            accepted=(
                wager.accepted
            ),
            resolved=(
                wager.resolved
            ),
            winner=wager.winner,
            loser=wager.loser,
        )

    def to_dict(self):
        return {
            "name":
                "serpent_lilith_drink_wager",
            "participants": list(
                self.participants
            ),
            "challenge": {
                "make_something_better":
                    self.make_something_better,
                "eligible_drinks": list(
                    self.eligible_drinks
                ),
                "existing_better_example":
                    self.existing_better_example,
            },
            "stakes": {
                "winner":
                    self.winner_stake,
                "loser":
                    self.loser_stake,
            },
            "proposed_by":
                self.proposed_by,
            "accepted_by":
                self.accepted_by,
            "accepted":
                self.accepted,
            "resolved":
                self.resolved,
            "winner":
                self.winner,
            "loser":
                self.loser,
        }


@dataclass(slots=True, frozen=True)
class SerpentLilithConversationStartedEvent:
    participants: tuple[str, ...] = (
        "serpent",
        "lilith",
    )

    name: str = field(
        default=(
            "serpent_and_lilith_"
            "begin_conversation"
        ),
        init=False,
    )

    bartender_present: bool = field(
        default=False,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "participants": list(
                self.participants
            ),
            "bartender_present":
                self.bartender_present,
        }


@dataclass(slots=True, frozen=True)
class SerpentLilithFirstDrinksTastedEvent:
    serpent_reaction: (
        FirstBarDrinkReactionState
    )
    lilith_reaction: (
        FirstBarDrinkReactionState
    )

    name: str = field(
        default=(
            "serpent_and_lilith_"
            "taste_first_drinks"
        ),
        init=False,
    )

    offered_by: str = field(
        default="serpent",
        init=False,
    )

    shared_with: str = field(
        default="lilith",
        init=False,
    )

    drinks: tuple[str, ...] = field(
        default=(
            "wine",
            "beer",
            "mead",
        ),
        init=False,
    )

    def __post_init__(self):
        for reaction in (
            self.serpent_reaction,
            self.lilith_reaction,
        ):
            if not isinstance(
                reaction,
                FirstBarDrinkReactionState,
            ):
                raise TypeError(
                    "First drink tasting "
                    "requires typed reaction "
                    "state objects."
                )

    def to_dict(self):
        return {
            "name": self.name,
            "offered_by":
                self.offered_by,
            "shared_with":
                self.shared_with,
            "drinks": list(
                self.drinks
            ),
            "serpent_reaction":
                self
                .serpent_reaction
                .to_dict(),
            "lilith_reaction":
                self
                .lilith_reaction
                .to_dict(),
        }


@dataclass(slots=True, frozen=True)
class SerpentProposesDrinkWagerEvent:
    wager: InitialBarDrinkWagerSnapshot

    name: str = field(
        default=(
            "serpent_proposes_"
            "drink_wager_to_lilith"
        ),
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.wager,
            InitialBarDrinkWagerSnapshot,
        ):
            raise TypeError(
                "Drink wager proposal event "
                "requires a typed wager snapshot."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "wager":
                self.wager.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class LilithAcceptsDrinkWagerEvent:
    wager: InitialBarDrinkWagerSnapshot

    name: str = field(
        default=(
            "lilith_accepts_drink_wager"
        ),
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.wager,
            InitialBarDrinkWagerSnapshot,
        ):
            raise TypeError(
                "Drink wager acceptance "
                "event requires a typed "
                "wager snapshot."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "wager":
                self.wager.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class SerpentLilithFirstConversationResult:
    tasting: (
        SerpentLilithFirstDrinksTastedEvent
    )
    wager: BarDrinkWager
    accepted: BarDrinkWager

    def __post_init__(self):
        if not isinstance(
            self.tasting,
            SerpentLilithFirstDrinksTastedEvent,
        ):
            raise TypeError(
                "First conversation result "
                "requires a typed tasting event."
            )

        if not isinstance(
            self.wager,
            BarDrinkWager,
        ):
            raise TypeError(
                "First conversation result "
                "requires a BarDrinkWager object."
            )

        if self.accepted is not self.wager:
            raise ValueError(
                "Accepted wager must preserve "
                "the wager object identity."
            )

    def to_dict(self):
        return {
            "tasting":
                self.tasting.to_dict(),
            "wager":
                self.wager.to_dict(),
            "accepted":
                self.accepted.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class SerpentLilithAgreeOnTableEvent:
    participants: tuple[str, ...] = (
        "serpent",
        "lilith",
    )

    name: str = field(
        default=(
            "serpent_and_lilith_"
            "agree_on_table"
        ),
        init=False,
    )

    agreed: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "participants": list(
                self.participants
            ),
            "agreed":
                self.agreed,
        }


@dataclass(slots=True, frozen=True)
class SerpentMovesToExistingTableEvent:
    destination: str

    name: str = field(
        default=(
            "serpent_moves_to_existing_table"
        ),
        init=False,
    )

    guest: str = field(
        default="serpent",
        init=False,
    )

    source: str = field(
        default="bar_counter",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "destination",
            str(self.destination),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "from": self.source,
            "to": self.destination,
        }
