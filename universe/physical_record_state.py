from copy import deepcopy
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CosmicHistoryEvent:
    name: str
    description: str

    def __post_init__(self):
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(
            self,
            "description",
            str(self.description),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
        }


@dataclass(slots=True, frozen=True)
class AtomicTimeStandard:
    name: str
    type: str
    state: str
    based_on: str
    isotope: object
    transition: str
    frequency_hz: int
    frequency_unit: str
    meaning: str
    future_use: tuple[str, ...]

    def __post_init__(self):
        for field_name in (
            "name",
            "type",
            "state",
            "based_on",
            "transition",
            "frequency_unit",
            "meaning",
        ):
            object.__setattr__(
                self,
                field_name,
                str(getattr(self, field_name)),
            )

        if not callable(
            getattr(self.isotope, "to_dict", None)
        ):
            raise TypeError(
                "Atomic time standard isotope must "
                "provide to_dict()."
            )

        object.__setattr__(
            self,
            "frequency_hz",
            int(self.frequency_hz),
        )
        object.__setattr__(
            self,
            "future_use",
            tuple(
                str(item)
                for item in self.future_use
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "based_on": self.based_on,
            "isotope": deepcopy(
                self.isotope.to_dict()
            ),
            "transition": self.transition,
            "frequency_hz": self.frequency_hz,
            "frequency_unit": self.frequency_unit,
            "meaning": self.meaning,
            "future_use": list(self.future_use),
        }


@dataclass(slots=True, frozen=True)
class RadioactiveDecayPattern:
    name: str
    type: str
    state: str
    parent_isotope: str
    parent_element: str
    parent_symbol: str
    daughter_product: str
    half_life_years: int | float
    half_life_precision: str
    time_scale: str
    use: str
    future_use: tuple[str, ...]

    def __post_init__(self):
        for field_name in (
            "name",
            "type",
            "state",
            "parent_isotope",
            "parent_element",
            "parent_symbol",
            "daughter_product",
            "half_life_precision",
            "time_scale",
            "use",
        ):
            object.__setattr__(
                self,
                field_name,
                str(getattr(self, field_name)),
            )

        object.__setattr__(
            self,
            "half_life_years",
            float(self.half_life_years),
        )
        object.__setattr__(
            self,
            "future_use",
            tuple(
                str(item)
                for item in self.future_use
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "parent_isotope": self.parent_isotope,
            "parent_element": self.parent_element,
            "parent_symbol": self.parent_symbol,
            "daughter_product": self.daughter_product,
            "half_life_years": self.half_life_years,
            "half_life_precision": self.half_life_precision,
            "time_scale": self.time_scale,
            "use": self.use,
            "future_use": list(self.future_use),
        }
