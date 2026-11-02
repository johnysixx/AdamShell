from dataclasses import dataclass, replace


@dataclass(frozen=True, slots=True)
class PrimordialIdentityCursor:
    scope: str
    star_serial: int = 0
    nebula_serial: int = 0

    def __post_init__(self):
        if not isinstance(self.scope, str) or not self.scope:
            raise ValueError(
                "Identity scope must be a nonempty string."
            )

        for name in ("star_serial", "nebula_serial"):
            value = getattr(self, name)

            if type(value) is not int:
                raise TypeError(
                    f"{name} must be an integer."
                )

            if value < 0:
                raise ValueError(
                    f"{name} cannot be negative."
                )

    def with_next_star(self):
        return replace(
            self,
            star_serial=self.star_serial + 1,
        )

    def with_next_nebula(self):
        return replace(
            self,
            nebula_serial=self.nebula_serial + 1,
        )

    @property
    def star_id(self):
        if self.star_serial == 0:
            raise RuntimeError(
                "No primordial star has been created."
            )

        return (
            f"{self.scope}:"
            f"primordial_star:{self.star_serial}"
        )

    @property
    def nebula_id(self):
        if self.nebula_serial == 0:
            raise RuntimeError(
                "No primordial nebula has been created."
            )

        return (
            f"{self.scope}:"
            f"primordial_nebula:{self.nebula_serial}"
        )

    def to_dict(self):
        return {
            "scope": self.scope,
            "star_serial": self.star_serial,
            "nebula_serial": self.nebula_serial,
        }

    @classmethod
    def from_mapping(cls, mapping):
        if not isinstance(mapping, dict):
            raise TypeError(
                "Identity cursor boundary requires a dict."
            )

        expected = {
            "scope",
            "star_serial",
            "nebula_serial",
        }

        if set(mapping) != expected:
            raise ValueError(
                "Incomplete or unexpected identity cursor fields."
            )

        return cls(
            scope=mapping["scope"],
            star_serial=mapping["star_serial"],
            nebula_serial=mapping["nebula_serial"],
        )
