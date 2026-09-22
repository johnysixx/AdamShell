from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EternalFlameSourceIdea:
    name: str
    type: str
    state: str

    def __post_init__(self):
        if not self.name:
            raise ValueError("Eternal Flame source name must not be empty")
        if not self.type:
            raise ValueError("Eternal Flame source type must not be empty")
        if not self.state:
            raise ValueError("Eternal Flame source state must not be empty")

    @classmethod
    def capture(cls, source_idea):
        required_attributes = (
            "name",
            "type",
            "state",
        )

        if isinstance(source_idea, dict) or not all(
            hasattr(source_idea, attribute)
            for attribute in required_attributes
        ):
            raise TypeError("Eternal Flame requires an idea source.")

        if source_idea.name != "eternal_fire":
            raise ValueError("Invalid idea source for Eternal Flame.")

        return cls(
            name=source_idea.name,
            type=source_idea.type,
            state=source_idea.state,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
        }


@dataclass(frozen=True, slots=True)
class EternalFlameHistoryRecord:
    name: str
    tick: object = None
    state: str | None = None
    source_idea: EternalFlameSourceIdea | None = None
    keeper: object = None

    @classmethod
    def already_burning(cls, *, state, tick=None):
        return cls(
            name="eternal_flame_already_burns",
            state=state,
            tick=tick,
        )

    @classmethod
    def ignited(cls, *, source_idea, keeper=None, tick=None):
        if not isinstance(source_idea, EternalFlameSourceIdea):
            raise TypeError(
                "Eternal Flame ignition record requires an "
                "EternalFlameSourceIdea object."
            )

        return cls(
            name="eternal_flame_ignited",
            source_idea=source_idea,
            keeper=keeper,
            tick=tick,
        )

    def to_dict(self):
        if self.name == "eternal_flame_already_burns":
            return {
                "name": self.name,
                "state": self.state,
                "tick": self.tick,
            }

        if self.name == "eternal_flame_ignited":
            return {
                "name": self.name,
                "source_idea": self.source_idea.to_dict(),
                "keeper": self.keeper,
                "tick": self.tick,
            }

        raise ValueError(
            f"Unknown Eternal Flame history record: {self.name}"
        )
