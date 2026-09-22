from dataclasses import dataclass


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
