from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class BouncerEntersBarWithGarfieldEvent:
    locations: tuple[str, ...] = (
        "outside_bar",
        "inside_bar",
    )

    name: str = field(
        default="bouncer_enters_bar_with_garfield",
        init=False,
    )
    bouncer: str = field(
        default="bouncer",
        init=False,
    )
    with_cat: str = field(
        default="garfield",
        init=False,
    )
    still_guards_entrance: bool = field(
        default=True,
        init=False,
    )
    present_inside: bool = field(
        default=True,
        init=False,
    )
    purpose: str = field(
        default="discuss_wager_judging",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "locations",
            tuple(
                str(location)
                for location
                in self.locations
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "bouncer": self.bouncer,
            "with": self.with_cat,
            "locations": list(
                self.locations
            ),
            "still_guards_entrance":
                self.still_guards_entrance,
            "present_inside":
                self.present_inside,
            "purpose": self.purpose,
        }


@dataclass(slots=True, frozen=True)
class SerpentExplainsWagerToBouncerEvent:
    participants: tuple[str, ...]
    contest: tuple[str, ...] = (
        "wine",
        "mead",
        "beer",
    )
    proposed_judges: tuple[str, ...] = (
        "bartender",
        "bouncer",
    )

    name: str = field(
        default="serpent_explains_wager_to_bouncer",
        init=False,
    )
    speaker: str = field(
        default="serpent",
        init=False,
    )
    listener: str = field(
        default="bouncer",
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

        object.__setattr__(
            self,
            "contest",
            tuple(
                str(drink)
                for drink
                in self.contest
            ),
        )

        object.__setattr__(
            self,
            "proposed_judges",
            tuple(
                str(judge)
                for judge
                in self.proposed_judges
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "listener": self.listener,
            "participants": list(
                self.participants
            ),
            "contest": list(
                self.contest
            ),
            "proposed_judges": list(
                self.proposed_judges
            ),
        }
