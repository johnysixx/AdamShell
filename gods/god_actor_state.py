from dataclasses import dataclass

from core.entity.social_entity import SocialEntity
from gods.gods_state import (
    GodMaskRegistry,
    GodsPermissions,
)


@dataclass(slots=True)
class GodDivineAttributes:
    aseity: bool = True
    eternity: bool = True
    transcendence: bool = True
    immanence: bool = True
    creative_authority: str = "potential"
    sovereignty: str = "potential"
    providence: str = "potential"
    omniscience: str = "potential"
    omnipotence: str = "potential"
    omnipresence: str = "potential"
    immutability: str = "limited_by_story_state"
    simplicity: str = "symbolic"
    perfect_goodness: str = "not_assumed"

    def to_dict(self):
        return {
            "aseity": self.aseity,
            "eternity": self.eternity,
            "transcendence": self.transcendence,
            "immanence": self.immanence,
            "creative_authority": self.creative_authority,
            "sovereignty": self.sovereignty,
            "providence": self.providence,
            "omniscience": self.omniscience,
            "omnipotence": self.omnipotence,
            "omnipresence": self.omnipresence,
            "immutability": self.immutability,
            "simplicity": self.simplicity,
            "perfect_goodness": self.perfect_goodness,
        }


@dataclass(frozen=True, slots=True)
class GodCreationLimits:
    limited_by_existence_pct: bool = True
    limited_by_creative_will: bool = True
    limited_by_current_reality_rules: bool = True

    def to_dict(self):
        return {
            "limited_by_existence_pct": self.limited_by_existence_pct,
            "limited_by_creative_will": self.limited_by_creative_will,
            "limited_by_current_reality_rules": (
                self.limited_by_current_reality_rules
            ),
        }


class GodEntity(SocialEntity):
    """God actor with protected object-state fields."""

    def __setattr__(self, name, value):
        if name == "masks":
            if not isinstance(value, GodMaskRegistry):
                raise TypeError(
                    "God masks require GodMaskRegistry."
                )

        elif name == "permissions":
            if not isinstance(value, GodsPermissions):
                raise TypeError(
                    "God permissions require GodsPermissions."
                )

        elif name == "creation_limits":
            if not isinstance(value, GodCreationLimits):
                raise TypeError(
                    "God creation limits require "
                    "GodCreationLimits."
                )

        elif name == "divine_attributes":
            if not isinstance(value, GodDivineAttributes):
                raise TypeError(
                    "God divine attributes require "
                    "GodDivineAttributes."
                )

        elif name == "active_mask":
            if (
                value is not None
                and not isinstance(value, str)
            ):
                raise TypeError(
                    "Active god mask must be a string "
                    "or None."
                )

        super().__setattr__(name, value)
