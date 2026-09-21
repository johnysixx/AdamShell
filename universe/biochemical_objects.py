from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class BiochemicalCompound:
    name: str
    compound_type: str
    requires: tuple[str, ...] = field(default_factory=tuple)
    future_use: tuple[str, ...] = field(default_factory=tuple)
    origin: str = "planetary_biochemistry"

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise TypeError("compound name must be a non-empty string")
        if not isinstance(self.compound_type, str) or not self.compound_type:
            raise TypeError("compound type must be a non-empty string")
        if not isinstance(self.origin, str) or not self.origin:
            raise TypeError("compound origin must be a non-empty string")

        requires = tuple(self.requires)
        future_use = tuple(self.future_use)

        if any(
            not isinstance(requirement, str) or not requirement
            for requirement in requires
        ):
            raise TypeError(
                "compound requirements must be non-empty strings"
            )
        if any(
            not isinstance(use, str) or not use
            for use in future_use
        ):
            raise TypeError(
                "compound future uses must be non-empty strings"
            )

        object.__setattr__(self, "requires", requires)
        object.__setattr__(self, "future_use", future_use)

    @property
    def type(self):
        return self.compound_type

    @property
    def state(self):
        return "possible"

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "requires": list(self.requires),
            "future_use": list(self.future_use),
            "origin": self.origin,
        }
