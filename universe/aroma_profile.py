from dataclasses import dataclass, field

from universe.aroma_composition import (
    AromaComposition,
    require_aroma_composition,
)


@dataclass
class AromaSurfaceResidue:

    source: str
    components: AromaComposition
    intensity: float = 1.0
    decay_rate: float = 0.03
    age_ticks: int = 0

    def __post_init__(self):
        self.components = require_aroma_composition(
            self.components,
            field_name=(
                "aroma surface residue components"
            ),
        )

        self.intensity = max(
            0.0,
            float(
                self.intensity
            ),
        )

        self.decay_rate = max(
            0.0,
            min(
                1.0,
                float(
                    self.decay_rate
                ),
            ),
        )

        self.age_ticks = max(
            0,
            int(
                self.age_ticks
            ),
        )

    def decay(
        self,
        ticks=1,
    ):
        ticks = max(
            0,
            int(
                ticks
            ),
        )

        self.age_ticks += ticks

        self.intensity *= (
            1.0
            - self.decay_rate
        ) ** ticks

        return self.intensity

    def to_dict(self):
        return {
            "source": self.source,
            "components": (
                self.components.to_dict()
            ),
            "intensity": self.intensity,
            "decay_rate": self.decay_rate,
            "age_ticks": self.age_ticks,
        }


@dataclass
class AromaProfile:

    identity: str
    base_components: AromaComposition = field(
        default_factory=AromaComposition.empty
    )
    base_intensity: float = 1.0
    surface_residues: list[
        AromaSurfaceResidue
    ] = field(
        default_factory=list
    )
    type: str = field(
        default="chemical_aroma_profile",
        init=False,
    )

    def __post_init__(self):
        self.base_components = (
            require_aroma_composition(
                self.base_components,
                field_name=(
                    "aroma profile base components"
                ),
            )
        )

        self.base_intensity = float(
            self.base_intensity
        )

        if self.base_intensity < 0.0:
            raise ValueError(
                "Aroma profile base intensity "
                "cannot be negative."
            )

        residues = list(
            self.surface_residues
        )

        if not all(
            isinstance(
                residue,
                AromaSurfaceResidue,
            )
            for residue in residues
        ):
            raise TypeError(
                "surface_residues must contain "
                "AromaSurfaceResidue objects."
            )

        self.surface_residues = residues

    def add_surface(
        self,
        source,
        components,
        intensity=1.0,
        decay_rate=0.03,
    ):
        components = (
            require_aroma_composition(
                components,
                field_name=(
                    "surface aroma components"
                ),
            )
        )

        residue = AromaSurfaceResidue(
            source=source,
            components=components,
            intensity=intensity,
            decay_rate=decay_rate,
        )

        self.surface_residues.append(
            residue
        )

        return residue

    def current(self):
        compositions = [
            self.base_components.scaled(
                self.base_intensity
            )
        ]

        for residue in self.surface_residues:
            compositions.append(
                residue.components.scaled(
                    residue.intensity
                )
            )

        return AromaComposition.combine(
            *compositions
        )

    def decay(
        self,
        ticks=1,
    ):
        ticks = max(
            0,
            int(
                ticks
            ),
        )

        survivors = []

        for residue in self.surface_residues:
            residue.decay(
                ticks=ticks
            )

            if residue.intensity > 0.001:
                survivors.append(
                    residue
                )

        self.surface_residues = survivors

        return self.current()

    def to_dict(self):
        return {
            "identity": self.identity,
            "base_components": (
                self.base_components.to_dict()
            ),
            "base_intensity": (
                self.base_intensity
            ),
            "surface_residues": [
                residue.to_dict()
                for residue
                in self.surface_residues
            ],
            "type": self.type,
        }
