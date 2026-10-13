from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    BarDrinkIdea,
    BarWineAssessment,
)


@dataclass(slots=True, frozen=True)
class SerpentModerateAcidityEvent:
    name: str = field(
        default=(
            "serpent_says_wine_needs_"
            "moderate_acidity"
        ),
        init=False,
    )
    speaker: str = field(
        default="serpent",
        init=False,
    )
    subject: str = field(
        default="wine",
        init=False,
    )
    agrees_acidity: bool = field(
        default=True,
        init=False,
    )
    too_much_acidity: str = field(
        default="bad",
        init=False,
    )
    desired_acidity: str = field(
        default="moderate",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "speaker": self.speaker,
            "subject": self.subject,
            "agrees_acidity":
                self.agrees_acidity,
            "too_much_acidity":
                self.too_much_acidity,
            "desired_acidity":
                self.desired_acidity,
        }


@dataclass(slots=True, frozen=True)
class SerpentModerateAcidityResult:
    idea: BarDrinkIdea
    event: SerpentModerateAcidityEvent

    def __post_init__(self):
        if not isinstance(
            self.idea,
            BarDrinkIdea,
        ):
            raise TypeError(
                "Moderate acidity result requires "
                "BarDrinkIdea."
            )

        if not isinstance(
            self.event,
            SerpentModerateAcidityEvent,
        ):
            raise TypeError(
                "Moderate acidity result requires "
                "SerpentModerateAcidityEvent."
            )

    def to_dict(self):
        return {
            "idea": self.idea.to_dict(),
            "event": self.event.to_dict(),
        }


@dataclass(slots=True, frozen=True)
class GodTastesExistingWineEvent:
    assessment: BarWineAssessment

    name: str = field(
        default="god_tastes_existing_wine",
        init=False,
    )
    guest: str = field(
        default="god",
        init=False,
    )
    drink: str = field(
        default="wine",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.assessment,
            BarWineAssessment,
        ):
            raise TypeError(
                "God wine tasting event requires "
                "BarWineAssessment."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "guest": self.guest,
            "drink": self.drink,
            "assessment":
                self.assessment.to_dict(),
        }
