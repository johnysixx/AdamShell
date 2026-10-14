from dataclasses import dataclass
from math import sqrt


@dataclass(
    slots=True,
    frozen=True,
)
class AromaComponent:

    name: str
    intensity: float

    def __post_init__(self):
        name = str(
            self.name
        ).strip()

        if not name:
            raise ValueError(
                "Aroma component name cannot be empty."
            )

        intensity = float(
            self.intensity
        )

        if intensity < 0.0:
            raise ValueError(
                "Aroma component intensity cannot be negative."
            )

        object.__setattr__(
            self,
            "name",
            name,
        )
        object.__setattr__(
            self,
            "intensity",
            intensity,
        )


@dataclass(
    slots=True,
    frozen=True,
)
class AromaComposition:

    entries: tuple[AromaComponent, ...] = ()

    def __post_init__(self):
        entries = tuple(
            self.entries
        )

        names = []

        for entry in entries:
            if not isinstance(
                entry,
                AromaComponent,
            ):
                raise TypeError(
                    "Aroma composition entries must use "
                    "AromaComponent objects."
                )

            if entry.name in names:
                raise ValueError(
                    "Aroma composition component names "
                    "must be unique."
                )

            names.append(
                entry.name
            )

        object.__setattr__(
            self,
            "entries",
            entries,
        )

    @classmethod
    def empty(cls):
        return cls()

    @classmethod
    def from_pairs(
        cls,
        *pairs,
    ):
        entries = []

        for pair in pairs:
            if (
                not isinstance(
                    pair,
                    tuple,
                )
                or len(pair) != 2
            ):
                raise TypeError(
                    "Aroma composition pairs must be "
                    "(name, intensity) tuples."
                )

            entries.append(
                AromaComponent(
                    name=pair[0],
                    intensity=pair[1],
                )
            )

        return cls(
            entries=tuple(
                entries
            )
        )

    @property
    def is_empty(self):
        return not any(
            entry.intensity > 0.0
            for entry in self.entries
        )

    @property
    def component_names(self):
        return tuple(
            entry.name
            for entry in self.entries
        )

    @property
    def total_intensity(self):
        return sum(
            entry.intensity
            for entry in self.entries
        )

    def amount(
        self,
        name,
    ):
        name = str(
            name
        )

        for entry in self.entries:
            if entry.name == name:
                return entry.intensity

        return 0.0

    def scaled(
        self,
        factor,
    ):
        factor = float(
            factor
        )

        if factor < 0.0:
            raise ValueError(
                "Aroma composition scale cannot be negative."
            )

        return AromaComposition(
            entries=tuple(
                AromaComponent(
                    name=entry.name,
                    intensity=(
                        entry.intensity
                        * factor
                    ),
                )
                for entry in self.entries
                if (
                    entry.intensity
                    * factor
                ) > 0.0
            )
        )

    @classmethod
    def combine(
        cls,
        *compositions,
    ):
        if not compositions:
            return cls.empty()

        for composition in compositions:
            require_aroma_composition(
                composition,
                field_name=(
                    "combined aroma composition"
                ),
            )

        names = []

        for composition in compositions:
            for entry in composition.entries:
                if entry.name not in names:
                    names.append(
                        entry.name
                    )

        return cls(
            entries=tuple(
                AromaComponent(
                    name=name,
                    intensity=sum(
                        composition.amount(
                            name
                        )
                        for composition
                        in compositions
                    ),
                )
                for name in names
                if sum(
                    composition.amount(
                        name
                    )
                    for composition
                    in compositions
                ) > 0.0
            )
        )

    def average_with(
        self,
        other,
    ):
        other = require_aroma_composition(
            other,
            field_name=(
                "averaged aroma composition"
            ),
        )

        names = list(
            self.component_names
        )

        for name in other.component_names:
            if name not in names:
                names.append(
                    name
                )

        return AromaComposition(
            entries=tuple(
                AromaComponent(
                    name=name,
                    intensity=(
                        self.amount(name)
                        + other.amount(name)
                    )
                    / 2.0,
                )
                for name in names
                if (
                    self.amount(name)
                    + other.amount(name)
                ) > 0.0
            )
        )

    def similarity_to(
        self,
        other,
    ):
        other = require_aroma_composition(
            other,
            field_name=(
                "aroma similarity composition"
            ),
        )

        names = list(
            self.component_names
        )

        for name in other.component_names:
            if name not in names:
                names.append(
                    name
                )

        if not names:
            return 0.0

        dot = sum(
            self.amount(name)
            * other.amount(name)
            for name in names
        )

        own_length = sqrt(
            sum(
                self.amount(name) ** 2
                for name in names
            )
        )

        other_length = sqrt(
            sum(
                other.amount(name) ** 2
                for name in names
            )
        )

        if (
            own_length == 0.0
            or other_length == 0.0
        ):
            return 0.0

        return max(
            0.0,
            min(
                1.0,
                dot
                / (
                    own_length
                    * other_length
                ),
            ),
        )

    def to_dict(self):
        return {
            entry.name: entry.intensity
            for entry in self.entries
        }


def require_aroma_composition(
    value,
    field_name="aroma composition",
):
    if not isinstance(
        value,
        AromaComposition,
    ):
        raise TypeError(
            f"{field_name} must use "
            "AromaComposition."
        )

    return value
