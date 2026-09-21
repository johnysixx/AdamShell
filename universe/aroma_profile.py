from dataclasses import dataclass, field


@dataclass
class AromaSurfaceResidue:
    source: str
    components: dict[str, float]
    intensity: float = 1.0
    decay_rate: float = 0.03
    age_ticks: int = 0

    def __post_init__(self):
        self.components = {
            str(component): float(amount)
            for component, amount in self.components.items()
        }
        self.intensity = max(0.0, float(self.intensity))
        self.decay_rate = max(0.0, min(1.0, float(self.decay_rate)))
        self.age_ticks = max(0, int(self.age_ticks))

    def decay(self, ticks=1):
        ticks = max(0, int(ticks))
        self.age_ticks += ticks
        self.intensity *= (1.0 - self.decay_rate) ** ticks
        return self.intensity

    def to_dict(self):
        return {
            "source": self.source,
            "components": dict(self.components),
            "intensity": self.intensity,
            "decay_rate": self.decay_rate,
            "age_ticks": self.age_ticks,
        }


@dataclass
class AromaProfile:
    identity: str
    base_components: dict[str, float] = field(default_factory=dict)
    base_intensity: float = 1.0
    surface_residues: list[AromaSurfaceResidue] = field(default_factory=list)
    type: str = field(
        default="chemical_aroma_profile",
        init=False,
    )

    def __post_init__(self):
        self.base_components = {
            str(component): float(amount)
            for component, amount in self.base_components.items()
        }
        self.base_intensity = float(self.base_intensity)

        if not all(
            isinstance(residue, AromaSurfaceResidue)
            for residue in self.surface_residues
        ):
            raise TypeError(
                "surface_residues must contain "
                "AromaSurfaceResidue objects."
            )

        self.surface_residues = list(self.surface_residues)

    def add_surface(
        self,
        source,
        components,
        intensity=1.0,
        decay_rate=0.03,
    ):
        residue = AromaSurfaceResidue(
            source=source,
            components=components,
            intensity=intensity,
            decay_rate=decay_rate,
        )
        self.surface_residues.append(residue)
        return residue

    def current(self):
        result = {}

        for component, amount in self.base_components.items():
            result[component] = (
                result.get(component, 0.0)
                + float(amount) * self.base_intensity
            )

        for residue in self.surface_residues:
            for component, amount in residue.components.items():
                result[component] = (
                    result.get(component, 0.0)
                    + float(amount) * residue.intensity
                )

        return result

    def decay(self, ticks=1):
        ticks = max(0, int(ticks))
        survivors = []

        for residue in self.surface_residues:
            residue.decay(ticks=ticks)
            if residue.intensity > 0.001:
                survivors.append(residue)

        self.surface_residues = survivors
        return self.current()

    def to_dict(self):
        return {
            "identity": self.identity,
            "base_components": dict(self.base_components),
            "base_intensity": self.base_intensity,
            "surface_residues": [
                residue.to_dict()
                for residue in self.surface_residues
            ],
            "type": self.type,
        }
