from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class GodMemoryNote:
    event: str

    def __post_init__(self):
        if not isinstance(self.event, str) or not self.event:
            raise TypeError("Memory note requires an event name.")


@dataclass(slots=True, frozen=True)
class GodMemorySnapshot:
    knowledge: tuple[str, ...] = ()
    observations: tuple[object, ...] = ()

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

        for observation in self.observations:
            self._validate_observation(observation)

    @staticmethod
    def _validate_observation(observation):
        if (
            isinstance(observation, dict)
            or not isinstance(
                getattr(observation, "event", None),
                str,
            )
            or not observation.event
        ):
            raise TypeError(
                "Research observation requires a typed "
                "object with an event name."
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
        )

    def with_observation(self, observation):
        self._validate_observation(observation)

        return GodMemorySnapshot(
            knowledge=self.knowledge,
            observations=self.observations + (observation,),
        )

    def observation_at(self, index):
        return self.observations[index]


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

    @property
    def record_count(self):
        return len(self._snapshot.observations)
