from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class WorldExistenceEntry:
    world: str
    percent: float

    def __post_init__(self):
        if not isinstance(self.world, str) or not self.world:
            raise TypeError(
                "Existence world must be a nonempty string."
            )

        object.__setattr__(
            self,
            "percent",
            float(self.percent),
        )


@dataclass(slots=True, frozen=True)
class WorldExistenceState:
    entries: tuple[WorldExistenceEntry, ...] = ()

    def __post_init__(self):
        if not isinstance(self.entries, tuple):
            raise TypeError(
                "World existence entries must be a tuple."
            )

        if any(
            not isinstance(entry, WorldExistenceEntry)
            for entry in self.entries
        ):
            raise TypeError(
                "World existence requires typed entries."
            )

        names = tuple(
            entry.world
            for entry in self.entries
        )

        if len(names) != len(set(names)):
            raise ValueError(
                "Duplicate existence world."
            )

    @classmethod
    def of(cls, **levels):
        return cls(
            entries=tuple(
                WorldExistenceEntry(
                    world=world,
                    percent=percent,
                )
                for world, percent in levels.items()
            )
        )

    @classmethod
    def from_mapping(cls, mapping):
        """Explicit deserialization boundary only."""
        if not isinstance(mapping, dict):
            raise TypeError(
                "WorldExistenceState.from_mapping "
                "requires a dictionary."
            )

        return cls(
            entries=tuple(
                WorldExistenceEntry(
                    world=world,
                    percent=percent,
                )
                for world, percent in mapping.items()
            )
        )

    def has_world(self, world):
        return any(
            entry.world == world
            for entry in self.entries
        )

    def percent_in(self, world):
        for entry in self.entries:
            if entry.world == world:
                return entry.percent

        return 0.0

    def with_percent(self, world, percent):
        updated = WorldExistenceEntry(
            world=world,
            percent=percent,
        )

        if self.has_world(world):
            entries = tuple(
                updated
                if entry.world == world
                else entry
                for entry in self.entries
            )
        else:
            entries = self.entries + (updated,)

        return WorldExistenceState(entries=entries)

    def strongest_world(self, native_world=None):
        if not self.entries:
            return native_world

        maximum = max(
            entry.percent
            for entry in self.entries
        )

        for entry in self.entries:
            if (
                entry.world == native_world
                and entry.percent == maximum
            ):
                return native_world

        for entry in self.entries:
            if entry.percent == maximum:
                return entry.world

        raise RuntimeError(
            "Cannot resolve strongest world."
        )

    def exists_anywhere(self):
        return any(
            entry.percent > 0.0
            for entry in self.entries
        )

    def to_dict(self):
        """Explicit serialization boundary only."""
        return {
            entry.world: entry.percent
            for entry in self.entries
        }
