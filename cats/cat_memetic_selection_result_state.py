from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatMemeExposureDeniedResult:
    reason: str

    name: str = field(
        default="cat_meme_exposure_denied",
        init=False,
    )

    exposed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatMythMemeticExposureResult:
    group_id: str
    myth_id: str
    adopted: tuple[str, ...]
    rejected: tuple[str, ...]
    fitness: float

    name: str = field(
        default="cat_myth_memetic_exposure",
        init=False,
    )

    exposed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "adopted",
            tuple(self.adopted),
        )

        object.__setattr__(
            self,
            "rejected",
            tuple(self.rejected),
        )

        object.__setattr__(
            self,
            "fitness",
            float(self.fitness),
        )


@dataclass(slots=True, frozen=True)
class CatInnovationMemeticExposureResult:
    group_id: str
    innovation_id: str
    adopted: tuple[str, ...]
    rejected: tuple[str, ...]
    fitness: float

    name: str = field(
        default="cat_innovation_memetic_exposure",
        init=False,
    )

    exposed: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "adopted",
            tuple(self.adopted),
        )

        object.__setattr__(
            self,
            "rejected",
            tuple(self.rejected),
        )

        object.__setattr__(
            self,
            "fitness",
            float(self.fitness),
        )


@dataclass(slots=True, frozen=True)
class CatMythMemeticSelectionResult:
    group_id: str
    surviving: tuple[str, ...]
    fading: tuple[str, ...]

    name: str = field(
        default="cat_myth_memetic_selection",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "surviving",
            tuple(self.surviving),
        )

        object.__setattr__(
            self,
            "fading",
            tuple(self.fading),
        )


@dataclass(slots=True, frozen=True)
class CatInnovationMemeticSelectionResult:
    group_id: str
    surviving: tuple[str, ...]
    fading: tuple[str, ...]

    name: str = field(
        default="cat_innovation_memetic_selection",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "surviving",
            tuple(self.surviving),
        )

        object.__setattr__(
            self,
            "fading",
            tuple(self.fading),
        )
