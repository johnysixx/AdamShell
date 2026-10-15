from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class PrimordialNebulaRemnant:
    source: str
    elemental_potentials: dict = field(
        default_factory=dict,
    )

    type: str = field(
        default="primordial_nebula_remnant",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "source",
            str(self.source),
        )

        normalized = {
            str(element): float(amount)
            for element, amount
            in self.elemental_potentials.items()
        }

        object.__setattr__(
            self,
            "elemental_potentials",
            normalized,
        )

    def to_dict(self):
        return {
            "type":
                self.type,
            "source":
                self.source,
            "elemental_potentials":
                dict(
                    self.elemental_potentials
                ),
        }


@dataclass(slots=True, frozen=True)
class PrimordialStellarEpochResult:
    primordial_nebula: object
    stars: tuple
    remnants: tuple

    def __post_init__(self):
        stars = tuple(
            self.stars
        )

        remnants = tuple(
            self.remnants
        )

        for remnant in remnants:
            if not isinstance(
                remnant,
                PrimordialNebulaRemnant,
            ):
                raise TypeError(
                    "Primordial stellar epoch "
                    "remnants must be "
                    "PrimordialNebulaRemnant."
                )

        object.__setattr__(
            self,
            "stars",
            stars,
        )

        object.__setattr__(
            self,
            "remnants",
            remnants,
        )
