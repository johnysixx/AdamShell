from copy import deepcopy
from dataclasses import dataclass, field


def _default_allowed_colors():
    return [
        "white",
        "black",
        "blue",
        "gray",
        "orange",
        "cream",
        "chocolate",
        "cinnamon",
        "lilac",
        "fawn",
        "tortoiseshell",
        "blue_tortoiseshell",
        "calico",
    ]


def _default_allowed_patterns():
    return [
        "solid",
        "tabby",
        "tuxedo",
        "bicolor",
        "tricolor",
        "pointed",
        "smoke",
        "shaded",
    ]


def _default_allowed_eye_colors():
    return [
        "blue",
        "green",
        "yellow",
        "gold",
        "amber",
        "orange",
        "copper",
        "hazel",
        "aqua",
        "odd_eyed",
    ]


def _default_access_rules():
    return {
        "can_access_anywhere": True,
        "access_via": [
            "boxes",
            "cat_doors",
        ],
    }


@dataclass(slots=True)
class CatsState:

    layer_type: str = "species_layer"
    status: str = "created"
    cats: list = field(default_factory=list)
    events: list = field(default_factory=list)
    tick_count: int = 0
    allowed_colors: list = field(
        default_factory=_default_allowed_colors
    )
    allowed_patterns: list = field(
        default_factory=_default_allowed_patterns
    )
    allowed_eye_colors: list = field(
        default_factory=_default_allowed_eye_colors
    )
    allowed_fur_lengths: list = field(
        default_factory=lambda: ["short", "long"]
    )
    allowed_sexes: list = field(
        default_factory=lambda: ["female", "male"]
    )
    default_idea_energy: int = 100
    access_rules: dict = field(
        default_factory=_default_access_rules
    )

    def to_dict(self):
        return {
            "type": self.layer_type,
            "state": self.status,
            "cats": list(self.cats),
            "events": deepcopy(self.events),
            "tick_count": self.tick_count,
            "allowed_colors": list(self.allowed_colors),
            "allowed_patterns": list(self.allowed_patterns),
            "allowed_eye_colors": list(self.allowed_eye_colors),
            "allowed_fur_lengths": list(
                self.allowed_fur_lengths
            ),
            "allowed_sexes": list(self.allowed_sexes),
            "default_idea_energy": self.default_idea_energy,
            "access_rules": deepcopy(self.access_rules),
        }
