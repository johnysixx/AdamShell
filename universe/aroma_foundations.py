from copy import deepcopy
from dataclasses import dataclass, field

from universe.aroma_composition import (
    AromaComposition,
    require_aroma_composition,
)


@dataclass(slots=True)
class AromaDefinition:

    name: str
    type: str
    components: AromaComposition = field(
        default_factory=AromaComposition.empty
    )
    natural_sources: tuple[str, ...] = ()
    molecule: str | None = None
    formula: str | None = None

    def __post_init__(self):
        self.components = (
            require_aroma_composition(
                self.components,
                field_name=(
                    "aroma definition components"
                ),
            )
        )

        self.natural_sources = tuple(
            self.natural_sources
        )

    def to_dict(self):
        result = {
            "name": self.name,
            "type": self.type,
            "components": (
                self.components.to_dict()
            ),
            "natural_sources": list(
                self.natural_sources
            ),
        }

        if self.molecule is not None:
            result[
                "molecule"
            ] = self.molecule

        if self.formula is not None:
            result[
                "formula"
            ] = self.formula

        return result


@dataclass(slots=True)
class AromaMixture:

    name: str
    type: str
    chemical_base: tuple[str, ...] = ()
    aromatic_components: tuple[str, ...] = ()
    aroma_profile: AromaComposition = field(
        default_factory=AromaComposition.empty
    )
    smells_similar_to: tuple[str, ...] = ()

    def __post_init__(self):
        self.chemical_base = tuple(
            self.chemical_base
        )

        self.aromatic_components = tuple(
            self.aromatic_components
        )

        self.aroma_profile = (
            require_aroma_composition(
                self.aroma_profile,
                field_name=(
                    "aroma mixture profile"
                ),
            )
        )

        self.smells_similar_to = tuple(
            self.smells_similar_to
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "chemical_base": list(
                self.chemical_base
            ),
            "aromatic_components": list(
                self.aromatic_components
            ),
            "aroma_profile": (
                self.aroma_profile.to_dict()
            ),
            "smells_similar_to": list(
                self.smells_similar_to
            ),
        }


class AromaFoundations:

    def __init__(
        self,
        universe,
    ):
        self.universe = universe

        self.aromas = {
            "berry_esters": AromaDefinition(
                name="berry_esters",
                type=(
                    "aromatic_compound_family"
                ),
                components=(
                    AromaComposition.from_pairs(
                        ("berry", 1.0),
                        ("fruit", 0.90),
                        ("sweet", 0.65),
                        ("floral", 0.20),
                    )
                ),
                natural_sources=(
                    "raspberries",
                    "berries",
                    "ripe_fruit",
                ),
            ),
            "vanillin": AromaDefinition(
                name="vanillin",
                type="aromatic_compound",
                components=(
                    AromaComposition.from_pairs(
                        ("vanilla", 1.0),
                        ("sweet", 0.70),
                        ("warm", 0.40),
                    )
                ),
                natural_sources=(
                    "vanilla",
                    "oak_aged_spirits",
                ),
            ),
            "oak_lactones": AromaDefinition(
                name="oak_lactones",
                type=(
                    "aromatic_compound_family"
                ),
                components=(
                    AromaComposition.from_pairs(
                        ("oak", 1.0),
                        ("woody", 0.80),
                        ("coconut", 0.25),
                    )
                ),
                natural_sources=(
                    "oak",
                    "oak_barrels",
                ),
            ),
            "caramel_notes": AromaDefinition(
                name="caramel_notes",
                type="aromatic_mixture",
                components=(
                    AromaComposition.from_pairs(
                        ("caramel", 1.0),
                        ("toasted_sugar", 0.75),
                        ("warm", 0.40),
                    )
                ),
                natural_sources=(
                    "caramelized_sugars",
                    "aged_rum",
                ),
            ),
            "ozone": AromaDefinition(
                name="ozone",
                type="molecular_aroma",
                molecule="ozone",
                formula="O3",
                components=(
                    AromaComposition.from_pairs(
                        ("ozone", 1.0),
                        ("sharp", 0.80),
                        ("electrical", 0.75),
                    )
                ),
                natural_sources=(
                    "electrical_discharge",
                    "lightning",
                    "cronenberg_manifestation",
                ),
            ),
        }

        self.mixtures = {
            "raspberry_rum": AromaMixture(
                name="raspberry_rum",
                type=(
                    "bar_aromatic_mixture"
                ),
                chemical_base=(
                    "ethanol",
                    "water",
                ),
                aromatic_components=(
                    "berry_esters",
                    "vanillin",
                    "oak_lactones",
                    "caramel_notes",
                ),
                aroma_profile=(
                    AromaComposition.from_pairs(
                        ("ethanol", 0.75),
                        ("berry", 1.0),
                        ("fruit", 0.85),
                        ("sweet", 0.65),
                        ("vanilla", 0.30),
                        ("oak", 0.22),
                        ("caramel", 0.25),
                        ("warm", 0.20),
                    )
                ),
                smells_similar_to=(
                    "ripe_raspberries",
                    "berry_esters",
                    "vanilla",
                    "oak_aged_spirits",
                    "caramelized_sugars",
                ),
            )
        }

        self.write_to_world()

    def get_aroma(
        self,
        name,
    ):
        return deepcopy(
            self.aromas.get(
                name
            )
        )

    def get_mixture(
        self,
        name,
    ):
        return deepcopy(
            self.mixtures.get(
                name
            )
        )

    def write_to_world(self):
        self.universe.world[
            "aroma_foundations"
        ] = {
            "type": (
                "chemical_aroma_foundations"
            ),
            "aromas": self.aromas,
            "mixtures": self.mixtures,
        }
