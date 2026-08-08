from copy import deepcopy


class AromaFoundations:

    def __init__(
        self,
        universe
    ):
        self.universe = universe

        self.aromas = {
            "berry_esters": {
                "type": "aromatic_compound_family",
                "components": {
                    "berry": 1.0,
                    "fruit": 0.90,
                    "sweet": 0.65,
                    "floral": 0.20
                },
                "natural_sources": [
                    "raspberries",
                    "berries",
                    "ripe_fruit"
                ]
            },

            "vanillin": {
                "type": "aromatic_compound",
                "components": {
                    "vanilla": 1.0,
                    "sweet": 0.70,
                    "warm": 0.40
                },
                "natural_sources": [
                    "vanilla",
                    "oak_aged_spirits"
                ]
            },

            "oak_lactones": {
                "type": "aromatic_compound_family",
                "components": {
                    "oak": 1.0,
                    "woody": 0.80,
                    "coconut": 0.25
                },
                "natural_sources": [
                    "oak",
                    "oak_barrels"
                ]
            },

            "caramel_notes": {
                "type": "aromatic_mixture",
                "components": {
                    "caramel": 1.0,
                    "toasted_sugar": 0.75,
                    "warm": 0.40
                },
                "natural_sources": [
                    "caramelized_sugars",
                    "aged_rum"
                ]
            },

            "ozone": {
                "type": "molecular_aroma",
                "molecule": "ozone",
                "formula": "O3",
                "components": {
                    "ozone": 1.0,
                    "sharp": 0.80,
                    "electrical": 0.75
                },
                "natural_sources": [
                    "electrical_discharge",
                    "lightning",
                    "cronenberg_manifestation"
                ]
            }
        }

        self.mixtures = {
            "raspberry_rum": {
                "name": "raspberry_rum",
                "type": "bar_aromatic_mixture",
                "chemical_base": [
                    "ethanol",
                    "water"
                ],
                "aromatic_components": [
                    "berry_esters",
                    "vanillin",
                    "oak_lactones",
                    "caramel_notes"
                ],
                "aroma_profile": {
                    "ethanol": 0.75,
                    "berry": 1.0,
                    "fruit": 0.85,
                    "sweet": 0.65,
                    "vanilla": 0.30,
                    "oak": 0.22,
                    "caramel": 0.25,
                    "warm": 0.20
                },
                "smells_similar_to": [
                    "ripe_raspberries",
                    "berry_esters",
                    "vanilla",
                    "oak_aged_spirits",
                    "caramelized_sugars"
                ]
            }
        }

        self.write_to_world()

    def get_aroma(
        self,
        name
    ):
        return deepcopy(
            self.aromas.get(name)
        )

    def get_mixture(
        self,
        name
    ):
        return deepcopy(
            self.mixtures.get(name)
        )

    def write_to_world(self):
        self.universe.world[
            "aroma_foundations"
        ] = {
            "type": (
                "chemical_aroma_foundations"
            ),
            "aromas": self.aromas,
            "mixtures": self.mixtures
        }