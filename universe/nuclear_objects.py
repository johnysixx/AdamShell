from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AtomicNucleus:
    name: str
    element_name: str
    protons: int
    neutrons: int
    type: str = "atomic_nucleus"
    state: str = "formed"
    future_use: tuple[str, ...] = (
        "elements",
        "atoms",
        "isotopes",
    )

    def __post_init__(self):
        if isinstance(self.protons, bool) or not isinstance(
            self.protons,
            int,
        ):
            raise TypeError("protons must be an integer count.")

        if isinstance(self.neutrons, bool) or not isinstance(
            self.neutrons,
            int,
        ):
            raise TypeError("neutrons must be an integer count.")

        if self.protons < 0:
            raise ValueError("protons cannot be negative.")

        if self.neutrons < 0:
            raise ValueError("neutrons cannot be negative.")

        object.__setattr__(
            self,
            "future_use",
            tuple(self.future_use),
        )

    @property
    def atomic_number(self):
        return self.protons

    @property
    def mass_number(self):
        return self.protons + self.neutrons

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "element_name": self.element_name,
            "protons": self.protons,
            "neutrons": self.neutrons,
            "atomic_number": self.atomic_number,
            "mass_number": self.mass_number,
            "future_use": list(self.future_use),
        }
