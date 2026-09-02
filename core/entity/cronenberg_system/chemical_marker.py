from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CronenbergChemicalMarker:

    molecule: str
    formula: str

    def __post_init__(self):
        object.__setattr__(
            self,
            "molecule",
            str(self.molecule),
        )
        object.__setattr__(
            self,
            "formula",
            str(self.formula),
        )
