from dataclasses import dataclass, replace

from core.entity.component_object import ComponentObject


@dataclass(frozen=True)
class CatBirthProfile:
    color: str
    fur_length: str
    pattern: str
    eye_color: str
    sex: str

    TRAITS = frozenset({
        "color",
        "fur_length",
        "pattern",
        "eye_color",
        "sex",
    })

    def with_trait(self, trait, value):
        if trait not in self.TRAITS:
            raise ValueError(
                f"Unknown cat birth trait: {trait!r}."
            )

        return replace(
            self,
            **{trait: value}
        )

    def trait_value(self, trait):
        if trait not in self.TRAITS:
            raise ValueError(
                f"Unknown cat birth trait: {trait!r}."
            )

        return getattr(self, trait)

    def to_dict(self):
        return {
            "color": self.color,
            "fur_length": self.fur_length,
            "pattern": self.pattern,
            "eye_color": self.eye_color,
            "sex": self.sex,
        }


@dataclass(frozen=True)
class CatCanonicalBirthResolution:
    matched: bool
    occurrence: int
    identity: str | None
    profile: CatBirthProfile
    special_birth_event: str | None
    woodoo_rebirth: bool = False
    woodoo_birth_number: int | None = None
    rebirth_probability: float | None = None
    forced_birth: bool = False
    forced_by: str | None = None

    def __post_init__(self):
        if not isinstance(
            self.profile,
            CatBirthProfile
        ):
            raise TypeError(
                "profile must be a CatBirthProfile object."
            )

    def to_dict(self):
        snapshot = {
            "matched": self.matched,
            "occurrence": self.occurrence,
            "identity": self.identity,
            "profile": self.profile.to_dict(),
            "special_birth_event": (
                self.special_birth_event
            ),
            "woodoo_rebirth": self.woodoo_rebirth,
        }

        if self.woodoo_birth_number is not None:
            snapshot["woodoo_birth_number"] = (
                self.woodoo_birth_number
            )

        if self.rebirth_probability is not None:
            snapshot["rebirth_probability"] = (
                self.rebirth_probability
            )

        if self.forced_birth:
            snapshot["forced_birth"] = True

        if self.forced_by is not None:
            snapshot["forced_by"] = self.forced_by

        return snapshot


class KittenEmbryo(ComponentObject):
    pass


class CatLitter(ComponentObject):
    pass
