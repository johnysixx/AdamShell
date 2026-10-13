from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrinkWager,
)


@dataclass(slots=True, frozen=True)
class DrinkWagerExplanationSnapshot:
    participants: tuple[str, ...]
    eligible_drinks: tuple[str, ...]
    accepted: bool
    resolved: bool
    wager_type: str | None

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
                "Drink wager snapshot requires "
                "BarDrinkWager."
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
            accepted=bool(
                wager.accepted
            ),
            resolved=bool(
                wager.resolved
            ),
            wager_type=wager.type,
        )

    def to_dict(self):
        result = {
            "participants": list(
                self.participants
            ),
            "eligible_drinks": list(
                self.eligible_drinks
            ),
            "accepted": self.accepted,
            "resolved": self.resolved,
        }

        if self.wager_type is not None:
            result["type"] = (
                self.wager_type
            )

        return result


@dataclass(slots=True, frozen=True)
class SerpentTellsGodAboutDrinkWagerEvent:
    wager: DrinkWagerExplanationSnapshot
    contest: tuple[str, ...] = (
        "wine",
        "mead",
        "beer",
    )

    name: str = field(
        default=(
            "serpent_tells_god_about_"
            "drink_wager"
        ),
        init=False,
    )
    speaker: str = field(
        default="serpent",
        init=False,
    )
    listener: str = field(
        default="god",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.wager,
            DrinkWagerExplanationSnapshot,
        ):
            raise TypeError(
                "Wager explanation requires "
                "DrinkWagerExplanationSnapshot."
            )

        object.__setattr__(
            self,
            "contest",
            tuple(
                str(drink)
                for drink
                in self.contest
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "listener": self.listener,
            "wager":
                self.wager.to_dict(),
            "contest": list(
                self.contest
            ),
        }


@dataclass(slots=True)
class SerpentOffersGodWagerParticipationEvent:
    accepted: bool | None = None

    name: str = field(
        default=(
            "serpent_offers_god_"
            "wager_participation"
        ),
        init=False,
    )
    offered_by: str = field(
        default="serpent",
        init=False,
    )
    offered_to: str = field(
        default="god",
        init=False,
    )

    def accept(self):
        self.accepted = True
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "offered_by": self.offered_by,
            "offered_to": self.offered_to,
            "accepted": self.accepted,
        }


@dataclass(slots=True, frozen=True)
class GodAcceptsDrinkWagerEvent:
    participants: tuple[str, ...]

    name: str = field(
        default="god_accepts_drink_wager",
        init=False,
    )
    participant: str = field(
        default="god",
        init=False,
    )
    resolved: bool = field(
        default=False,
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
            "participant": self.participant,
            "participants": list(
                self.participants
            ),
            "resolved": self.resolved,
        }
