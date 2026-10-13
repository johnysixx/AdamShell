from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class SerpentLeavesTableForBarEvent:
    name: str = field(
        default="serpent_leaves_table_for_bar",
        init=False,
    )
    guest: str = field(
        default="serpent",
        init=False,
    )
    reason: str = field(
        default="nothing_good_left_to_drink",
        init=False,
    )
    remaining_drink: str = field(
        default="bad_beer",
        init=False,
    )
    from_location: str = field(
        default="table",
        init=False,
    )
    to_location: str = field(
        default="bar_counter",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "reason": self.reason,
            "remaining_drink":
                self.remaining_drink,
            "from": self.from_location,
            "to": self.to_location,
        }


@dataclass(slots=True, frozen=True)
class LilithGodContinueTalkingAtTableEvent:
    participants: tuple[str, ...] = (
        "lilith",
        "god",
    )

    name: str = field(
        default=(
            "lilith_and_god_continue_"
            "talking_at_table"
        ),
        init=False,
    )
    serpent_present: bool = field(
        default=False,
        init=False,
    )
    new_conclusion: str | None = field(
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
            "serpent_present":
                self.serpent_present,
            "new_conclusion":
                self.new_conclusion,
        }
