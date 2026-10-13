from dataclasses import dataclass, field

from idea_entities.archetype_state import (
    ArchetypePrincipleState,
    IdeaEntityAccessProfile,
)


@dataclass(slots=True, frozen=True)
class LilithBornEvent:
    principle: ArchetypePrincipleState
    access: IdeaEntityAccessProfile

    name: str = field(
        default="lilith_born",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.principle,
            ArchetypePrincipleState,
        ):
            raise TypeError(
                "Lilith principle must be "
                "ArchetypePrincipleState."
            )

        if not isinstance(
            self.access,
            IdeaEntityAccessProfile,
        ):
            raise TypeError(
                "Lilith access must be "
                "IdeaEntityAccessProfile."
            )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class LilithEnteredBarEvent:
    name: str = field(
        default="lilith_entered_bar",
        init=False,
    )
    lilith: str = field(
        default="lilith",
        init=False,
    )
    destination: str = field(
        default="bar",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
        }


@dataclass(slots=True, frozen=True)
class LilithEntryResult:
    lilith: object
    principle: ArchetypePrincipleState
    access: IdeaEntityAccessProfile
    born: LilithBornEvent
    entered: LilithEnteredBarEvent

    def __post_init__(self):
        if not isinstance(
            self.principle,
            ArchetypePrincipleState,
        ):
            raise TypeError(
                "Lilith entry principle must "
                "be object state."
            )

        if not isinstance(
            self.access,
            IdeaEntityAccessProfile,
        ):
            raise TypeError(
                "Lilith entry access must "
                "be object state."
            )

        if not isinstance(
            self.born,
            LilithBornEvent,
        ):
            raise TypeError(
                "Lilith birth must be "
                "object state."
            )

        if not isinstance(
            self.entered,
            LilithEnteredBarEvent,
        ):
            raise TypeError(
                "Lilith bar entry must be "
                "object state."
            )

        if (
            getattr(
                self.lilith,
                "principle",
                None,
            )
            is not self.principle
        ):
            raise ValueError(
                "Lilith entry principle identity "
                "must be preserved."
            )

        if (
            getattr(
                self.lilith,
                "access",
                None,
            )
            is not self.access
        ):
            raise ValueError(
                "Lilith entry access identity "
                "must be preserved."
            )
