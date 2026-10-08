from dataclasses import dataclass, field

from .cat_access_rules import CatAccessRules


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
    access_rules: CatAccessRules = field(
        default_factory=CatAccessRules
    )
