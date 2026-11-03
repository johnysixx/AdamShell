from dataclasses import dataclass

from idea_universe.primordial_idea_star_state import (
    PrimordialIdeaStarState,
)
from idea_universe.primordial_stellar_state import (
    PrimordialNebulaRemnant,
)


def _require_id(object_id):
    if (
        not isinstance(object_id, str)
        or not object_id.strip()
    ):
        raise ValueError(
            "Primordial history requires canonical ID."
        )


@dataclass(frozen=True, slots=True)
class PrimordialRemnantCreation:
    source_star_id: str
    source: str
    elemental_potentials: tuple[tuple[str, float], ...]

    def __post_init__(self):
        _require_id(self.source_star_id)

        if not isinstance(self.source, str):
            raise TypeError(
                "Remnant source must be a string."
            )

        if not isinstance(
            self.elemental_potentials,
            tuple,
        ):
            raise TypeError(
                "Remnant potentials must be a tuple."
            )

        names = []

        for item in self.elemental_potentials:
            if not isinstance(item, tuple) or len(item) != 2:
                raise TypeError(
                    "Each remnant potential must be a pair."
                )

            name, amount = item

            if not isinstance(name, str):
                raise TypeError(
                    "Element name must be a string."
                )

            if type(amount) is not float:
                raise TypeError(
                    "Element amount must be a float."
                )

            names.append(name)

        if len(names) != len(set(names)):
            raise ValueError(
                "Duplicate remnant elements."
            )

    @classmethod
    def from_remnant(cls, remnant, *, source_star_id):
        if not isinstance(
            remnant,
            PrimordialNebulaRemnant,
        ):
            raise TypeError(
                "Expected PrimordialNebulaRemnant."
            )

        potentials = tuple(
            sorted(
                (
                    str(name),
                    float(amount),
                )
                for name, amount
                in remnant.elemental_potentials.items()
            )
        )

        return cls(
            source_star_id=source_star_id,
            source=remnant.source,
            elemental_potentials=potentials,
        )

    def to_remnant(self):
        return PrimordialNebulaRemnant(
            source=self.source,
            elemental_potentials=dict(
                self.elemental_potentials
            ),
        )


@dataclass(frozen=True, slots=True)
class PrimordialStarCreated:
    object_id: str

    def __post_init__(self):
        _require_id(self.object_id)


@dataclass(frozen=True, slots=True)
class PrimordialStarTransition:
    object_id: str
    state: PrimordialIdeaStarState

    def __post_init__(self):
        _require_id(self.object_id)

        if not isinstance(
            self.state,
            PrimordialIdeaStarState,
        ):
            raise TypeError(
                "Star transition requires enum state."
            )


@dataclass(frozen=True, slots=True)
class PrimordialNebulaCreated:
    object_id: str
    remnants: tuple[PrimordialRemnantCreation, ...]

    def __post_init__(self):
        _require_id(self.object_id)

        if not isinstance(self.remnants, tuple):
            raise TypeError(
                "Nebula remnants must be a tuple."
            )

        if any(
            not isinstance(
                remnant,
                PrimordialRemnantCreation,
            )
            for remnant in self.remnants
        ):
            raise TypeError(
                "Nebula creation requires typed remnants."
            )


_NEBULA_PHYSICS_OPERATIONS = frozenset({
    "set_size",
    "form_hydrocarbons",
    "form_liquid_hydrocarbons",
    "record_liquid_hydrocarbon_level",
    "mine_liquid_hydrocarbons",
    "tick",
})


@dataclass(frozen=True, slots=True)
class PrimordialNebulaPhysicsEvent:
    object_id: str
    operation: str
    value: float | None = None
    result: float | int | None = None

    def __post_init__(self):
        _require_id(self.object_id)

        if self.operation not in _NEBULA_PHYSICS_OPERATIONS:
            raise ValueError(
                "Unsupported primordial nebula operation."
            )

        requires_value = self.operation in {
            "set_size",
            "record_liquid_hydrocarbon_level",
            "mine_liquid_hydrocarbons",
        }

        if requires_value:
            if (
                isinstance(self.value, bool)
                or not isinstance(self.value, (int, float))
            ):
                raise TypeError(
                    "Nebula operation requires numeric value."
                )
        elif self.value is not None:
            raise ValueError(
                "Unexpected nebula operation value."
            )

        if self.operation == "tick":
            if (
                type(self.result) is not int
                or self.result < 1
            ):
                raise TypeError(
                    "Nebula tick result must be positive integer."
                )
        elif (
            isinstance(self.result, bool)
            or not isinstance(self.result, (int, float))
        ):
            raise TypeError(
                "Nebula operation requires numeric result."
            )


_CREATION_EVENTS = (
    PrimordialStarCreated,
    PrimordialStarTransition,
    PrimordialNebulaCreated,
    PrimordialNebulaPhysicsEvent,
)


@dataclass(frozen=True, slots=True)
class PrimordialCreationHistory:
    scope: str
    events: tuple = ()

    def __post_init__(self):
        if not isinstance(self.scope, str) or not self.scope:
            raise ValueError(
                "Creation history requires a scope."
            )

        if not isinstance(self.events, tuple):
            raise TypeError(
                "Creation history events must be a tuple."
            )

        if any(
            type(event) not in _CREATION_EVENTS
            for event in self.events
        ):
            raise TypeError(
                "Unsupported primordial creation event."
            )

    def with_event(self, event):
        if type(event) not in _CREATION_EVENTS:
            raise TypeError(
                "Unsupported primordial creation event."
            )

        return PrimordialCreationHistory(
            scope=self.scope,
            events=self.events + (event,),
        )
