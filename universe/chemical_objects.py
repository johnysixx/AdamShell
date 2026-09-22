from dataclasses import dataclass, field
from types import MappingProxyType
from collections.abc import Mapping


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
    origin: str | None = None
    requires: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if self.atomic_number <= 0:
            raise ValueError("Atomic number must be positive")

        object.__setattr__(
            self,
            "future_use",
            tuple(self.future_use),
        )
        object.__setattr__(
            self,
            "requires",
            tuple(self.requires),
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
        if self.origin is not None:
            snapshot["origin"] = self.origin
        if self.requires:
            snapshot["requires"] = list(self.requires)

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


@dataclass(frozen=True, slots=True)
class ChemicalMolecule:
    name: str
    formula: str
    components: Mapping[ChemicalElement, int]
    category: str
    meaning: str
    future_use: tuple[str, ...] = field(default_factory=tuple)
    functional_group: str | None = None
    functional_group_symbol: str | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Molecule name must not be empty")
        if not self.formula:
            raise ValueError("Molecule formula must not be empty")
        if not isinstance(self.components, Mapping):
            raise TypeError(
                "components must be an element-to-count mapping"
            )
        if not self.components:
            raise ValueError("Molecule must contain at least one element")

        normalized_components = {}
        for element, count in self.components.items():
            if not isinstance(element, ChemicalElement):
                raise TypeError(
                    "Molecule component keys must be ChemicalElement objects"
                )
            if not isinstance(count, int) or isinstance(count, bool):
                raise TypeError("Molecule component counts must be integers")
            if count <= 0:
                raise ValueError("Molecule component counts must be positive")
            normalized_components[element] = count

        object.__setattr__(
            self,
            "components",
            MappingProxyType(normalized_components),
        )
        object.__setattr__(
            self,
            "future_use",
            tuple(self.future_use),
        )

        if (
            self.functional_group_symbol is not None
            and self.functional_group is None
        ):
            raise ValueError(
                "functional_group_symbol requires functional_group"
            )

    @property
    def type(self):
        return "molecule"

    @property
    def state(self):
        return "formed"

    @property
    def atom_count(self):
        return sum(self.components.values())

    def component_count(self, element_name):
        for element, count in self.components.items():
            if element.name == element_name:
                return count
        return 0

    def to_dict(self):
        snapshot = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "formula": self.formula,
            "components": {
                element.name: count
                for element, count in self.components.items()
            },
            "category": self.category,
            "meaning": self.meaning,
            "future_use": list(self.future_use),
        }

        if self.functional_group is not None:
            snapshot["functional_group"] = self.functional_group
        if self.functional_group_symbol is not None:
            snapshot["functional_group_symbol"] = (
                self.functional_group_symbol
            )

        return snapshot
