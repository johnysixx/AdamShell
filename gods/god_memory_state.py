from dataclasses import dataclass, fields, is_dataclass
from enum import Enum

from quantum.director_state import QuantumDirectorRecord


@dataclass(slots=True, frozen=True)
class GodMemoryNote:
    event: str

    def __post_init__(self):
        if not isinstance(self.event, str) or not self.event:
            raise TypeError("Memory note requires an event name.")



_SCALAR_TYPES = (
    str,
    int,
    float,
    bool,
    type(None),
)

_MISSING = object()


def _historical_scalar(value):
    if isinstance(value, Enum):
        value = value.value

    if type(value) in _SCALAR_TYPES:
        return value

    return _MISSING


@dataclass(slots=True, frozen=True)
class GodHistoricalValue:
    name: str
    value: str | int | float | bool | None

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise TypeError(
                "Historical value requires a field name."
            )

        if type(self.value) not in _SCALAR_TYPES:
            raise TypeError(
                "Historical value must be an immutable scalar."
            )


@dataclass(slots=True, frozen=True)
class GodObservationFact:
    event: str
    entries: tuple[GodHistoricalValue, ...] = ()

    def __post_init__(self):
        if not isinstance(self.event, str) or not self.event:
            raise TypeError(
                "Historical observation requires event name."
            )

        if not isinstance(self.entries, tuple):
            raise TypeError(
                "Historical values must be a tuple."
            )

        if any(
            not isinstance(value, GodHistoricalValue)
            for value in self.entries
        ):
            raise TypeError(
                "Historical facts require typed values."
            )

        names = tuple(value.name for value in self.entries)

        if len(names) != len(set(names)):
            raise ValueError(
                "Historical observation contains duplicate fields."
            )

    def value_for(self, name):
        for value in self.entries:
            if value.name == name:
                return value.value

        raise KeyError(name)

    @staticmethod
    def _capture_reference(name, reference):
        if isinstance(reference, dict):
            raise TypeError(
                "Historical references must be objects."
            )

        captured = [
            GodHistoricalValue(
                name=name + ".class",
                value=(
                    type(reference).__module__
                    + "."
                    + type(reference).__qualname__
                ),
            )
        ]

        for attribute in (
            "id",
            "name",
            "type",
            "source",
            "state",
            "stage",
            "size",
            "material",
            "amount",
            "current_liquid_hydrocarbon_level",
        ):
            raw = getattr(
                reference,
                attribute,
                _MISSING,
            )

            value = _historical_scalar(raw)

            if value is _MISSING:
                continue

            captured.append(
                GodHistoricalValue(
                    name=name + "." + attribute,
                    value=value,
                )
            )

        potentials = getattr(
            reference,
            "elemental_potentials",
            None,
        )

        if isinstance(potentials, dict):
            for element, amount in sorted(
                potentials.items()
            ):
                if not isinstance(element, str):
                    raise TypeError(
                        "Historical element names must be strings."
                    )

                frozen_amount = _historical_scalar(amount)

                if frozen_amount is _MISSING:
                    raise TypeError(
                        "Historical element amounts must "
                        "be immutable scalars."
                    )

                captured.append(
                    GodHistoricalValue(
                        name=(
                            name
                            + ".elemental_potentials."
                            + element
                        ),
                        value=frozen_amount,
                    )
                )

        return tuple(captured)

    @classmethod
    def capture(cls, observation):
        values = []

        for field in fields(observation):
            if field.name == "event":
                continue

            raw = getattr(
                observation,
                field.name,
            )

            scalar = _historical_scalar(raw)

            if scalar is not _MISSING:
                values.append(
                    GodHistoricalValue(
                        name=field.name,
                        value=scalar,
                    )
                )

                continue

            if field.name not in (
                "subject",
                "remnant",
                "met",
                "sample",
            ):
                raise TypeError(
                    "Unsupported historical observation field: "
                    + field.name
                )

            values.extend(
                cls._capture_reference(
                    field.name,
                    raw,
                )
            )

        return cls(
            event=observation.event,
            entries=tuple(values),
        )


@dataclass(slots=True, frozen=True)
class GodMemorySnapshot:
    knowledge: tuple[str, ...] = ()
    observations: tuple[object, ...] = ()
    facts: tuple[GodObservationFact, ...] = ()

    def __post_init__(self):
        if not isinstance(self.knowledge, tuple):
            raise TypeError("Knowledge must be a tuple.")

        if not isinstance(self.observations, tuple):
            raise TypeError("Observations must be a tuple.")

        if any(
            not isinstance(item, str) or not item
            for item in self.knowledge
        ):
            raise TypeError("Knowledge requires strings.")

        if len(self.knowledge) != len(set(self.knowledge)):
            raise ValueError("Knowledge contains duplicates.")

        if not isinstance(self.facts, tuple):
            raise TypeError(
                "Historical facts must be a tuple."
            )

        if len(self.facts) != len(self.observations):
            raise ValueError(
                "Observations and historical facts "
                "must have matching lengths."
            )

        if any(
            not isinstance(fact, GodObservationFact)
            for fact in self.facts
        ):
            raise TypeError(
                "Historical facts require GodObservationFact."
            )

        for observation in self.observations:
            self._validate_observation(observation)

    @staticmethod
    def _validate_observation(observation):
        if not isinstance(
            observation,
            (GodMemoryNote, QuantumDirectorRecord),
        ):
            raise TypeError(
                "Research observation requires "
                "GodMemoryNote or QuantumDirectorRecord."
            )

        params = getattr(
            type(observation),
            "__dataclass_params__",
            None,
        )

        if (
            not is_dataclass(observation)
            or params is None
            or not params.frozen
        ):
            raise TypeError(
                "Research observation must be "
                "a frozen dataclass."
            )

        if (
            not isinstance(
                getattr(observation, "event", None),
                str,
            )
            or not observation.event
        ):
            raise TypeError(
                "Research observation requires "
                "a nonempty event name."
            )

    def knows(self, finding):
        return finding in self.knowledge

    def with_knowledge(self, finding):
        if not isinstance(finding, str) or not finding:
            raise TypeError(
                "Knowledge finding must be a string."
            )

        if self.knows(finding):
            return self

        return GodMemorySnapshot(
            knowledge=self.knowledge + (finding,),
            observations=self.observations,
            facts=self.facts,
        )

    def with_observation(self, observation):
        self._validate_observation(observation)

        fact = GodObservationFact.capture(
            observation
        )

        return GodMemorySnapshot(
            knowledge=self.knowledge,
            observations=self.observations + (observation,),
            facts=self.facts + (fact,),
        )

    def observation_at(self, index):
        return self.observations[index]

    def fact_at(self, index):
        return self.facts[index]


class GodSharedMemory:
    """Stable shared owner of immutable memory snapshots."""

    __slots__ = ("_snapshot",)

    def __init__(self, snapshot=None):
        if snapshot is None:
            snapshot = GodMemorySnapshot()

        self._snapshot = snapshot

    def __setattr__(self, name, value):
        if (
            name == "_snapshot"
            and not isinstance(value, GodMemorySnapshot)
        ):
            raise TypeError(
                "Shared memory requires GodMemorySnapshot."
            )

        super().__setattr__(name, value)

    @property
    def state(self):
        return self._snapshot

    def knows(self, finding):
        return self._snapshot.knows(finding)

    def learn(self, finding):
        self._snapshot = self._snapshot.with_knowledge(finding)
        return self._snapshot

    def record(self, observation):
        self._snapshot = (
            self._snapshot.with_observation(observation)
        )
        return observation

    def record_at(self, index):
        return self._snapshot.observation_at(index)

    def fact_at(self, index):
        return self._snapshot.fact_at(index)

    @property
    def record_count(self):
        return len(self._snapshot.observations)
