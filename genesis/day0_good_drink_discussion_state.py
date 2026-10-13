from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrinkDiscussion,
)


@dataclass(slots=True, frozen=True)
class SerpentLilithGoodDrinkDiscussionStartedEvent:
    participants: tuple[str, ...]
    subjects: tuple[str, ...]
    question: str
    resolved: bool

    name: str = field(
        default=(
            "serpent_lilith_good_"
            "drink_discussion"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "participants",
            tuple(
                str(value)
                for value
                in self.participants
            ),
        )

        object.__setattr__(
            self,
            "subjects",
            tuple(
                str(value)
                for value
                in self.subjects
            ),
        )

        object.__setattr__(
            self,
            "question",
            str(
                self.question
            ),
        )

        object.__setattr__(
            self,
            "resolved",
            bool(
                self.resolved
            ),
        )

    @classmethod
    def from_discussion(
        cls,
        discussion,
    ):
        if not isinstance(
            discussion,
            BarDrinkDiscussion,
        ):
            raise TypeError(
                "Discussion start event requires "
                "BarDrinkDiscussion."
            )

        return cls(
            participants=(
                discussion.participants
            ),
            subjects=(
                discussion.subjects
            ),
            question=(
                discussion.question
            ),
            resolved=(
                discussion.resolved
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "participants": list(
                self.participants
            ),
            "subjects": list(
                self.subjects
            ),
            "question": self.question,
            "ideas": [],
            "resolved": self.resolved,
        }
