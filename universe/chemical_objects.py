from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ChemicalElement:
    name: str
    symbol: str
    atomic_number: int
    official: bool
    discovered: bool
    state: str
    future_use: tuple[str, ...] = field(default_factory=tuple)
    temporary_systematic_name: bool = False

    def __post_init__(self):
        if self.atomic_number <= 0:
            raise ValueError("Atomic number must be positive")

        object.__setattr__(
            self,
            "future_use",
            tuple(self.future_use),
        )

    @property
    def type(self):
        return "chemical_element"

    @property
    def protons(self):
        return self.atomic_number

    def to_dict(self):
        snapshot = {
            "name": self.name,
            "symbol": self.symbol,
            "type": self.type,
            "state": self.state,
            "atomic_number": self.atomic_number,
            "protons": self.protons,
            "official": self.official,
            "discovered": self.discovered,
            "future_use": list(self.future_use),
        }

        if self.temporary_systematic_name:
            snapshot["temporary_systematic_name"] = True

        return snapshot


@dataclass(frozen=True, slots=True)
class Isotope:
    element: ChemicalElement
    mass_number: int
    stability: str
    future_use: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not isinstance(self.element, ChemicalElement):
            raise TypeError("element must be a ChemicalElement object")
        if self.mass_number < self.element.atomic_number:
            raise ValueError(
                "Mass number cannot be smaller than atomic number"
            )

        object.__setattr__(
            self,
            "future_use",
            tuple(self.future_use),
        )

    @property
    def name(self):
        return f"{self.element.name}_{self.mass_number}"

    @property
    def type(self):
        return "isotope"

    @property
    def state(self):
        return "formed"

    @property
    def element_name(self):
        return self.element.name

    @property
    def symbol(self):
        return self.element.symbol

    @property
    def atomic_number(self):
        return self.element.atomic_number

    @property
    def protons(self):
        return self.atomic_number

    @property
    def neutrons(self):
        return self.mass_number - self.atomic_number

    @property
    def electrons_if_neutral_atom(self):
        return self.atomic_number

    @property
    def official_element(self):
        return self.element.official

    @property
    def discovered_element(self):
        return self.element.discovered

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "element_name": self.element_name,
            "symbol": self.symbol,
            "atomic_number": self.atomic_number,
            "mass_number": self.mass_number,
            "protons": self.protons,
            "neutrons": self.neutrons,
            "electrons_if_neutral_atom": (
                self.electrons_if_neutral_atom
            ),
            "stability": self.stability,
            "official_element": self.official_element,
            "discovered_element": self.discovered_element,
            "future_use": list(self.future_use),
        }


@dataclass(frozen=True, slots=True)
class NeutralAtom:
    element: ChemicalElement
    future_use: tuple[str, ...] = (
        "isotopes",
        "molecules",
        "materials",
    )

    def __post_init__(self):
        if not isinstance(self.element, ChemicalElement):
            raise TypeError("element must be a ChemicalElement object")

        object.__setattr__(
            self,
            "future_use",
            tuple(self.future_use),
        )

    @property
    def name(self):
        return f"{self.element.name}_atom"

    @property
    def type(self):
        return "neutral_atom"

    @property
    def state(self):
        return "formed"

    @property
    def element_name(self):
        return self.element.name

    @property
    def symbol(self):
        return self.element.symbol

    @property
    def atomic_number(self):
        return self.element.atomic_number

    @property
    def protons(self):
        return self.atomic_number

    @property
    def electrons(self):
        return self.atomic_number

    @property
    def net_charge(self):
        return 0

    @property
    def official_element(self):
        return self.element.official

    @property
    def discovered_element(self):
        return self.element.discovered

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "element_name": self.element_name,
            "symbol": self.symbol,
            "atomic_number": self.atomic_number,
            "protons": self.protons,
            "electrons": self.electrons,
            "net_charge": self.net_charge,
            "official_element": self.official_element,
            "discovered_element": self.discovered_element,
            "future_use": list(self.future_use),
        }
