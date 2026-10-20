from dataclasses import dataclass, field

from cats.feline_ability_state import (
    FelineAbilityState,
)
from cats.feline_awareness_state import (
    FelineAwarenessState,
)


@dataclass(slots=True)
class FelineAwarenessRegistry:

    _records: list = field(
        default_factory=list
    )

    @property
    def is_empty(
        self,
    ):
        return not self._records

    def store(
        self,
        awareness,
    ):
        if not isinstance(
            awareness,
            FelineAwarenessState,
        ):
            raise TypeError(
                "Feline awareness registry requires "
                "FelineAwarenessState."
            )

        for index, current in enumerate(
            self._records
        ):
            if not isinstance(
                current,
                FelineAwarenessState,
            ):
                raise TypeError(
                    "Feline awareness registry "
                    "contains invalid runtime state."
                )

            if current.name == awareness.name:
                self._records[
                    index
                ] = awareness

                return awareness

        self._records.append(
            awareness
        )

        return awareness

    def record(
        self,
        knowledge_name,
    ):
        knowledge_name = str(
            knowledge_name
        )

        for awareness in self.records():
            if awareness.name == knowledge_name:
                return awareness

        return None

    def records(
        self,
    ):
        for awareness in self._records:
            if not isinstance(
                awareness,
                FelineAwarenessState,
            ):
                raise TypeError(
                    "Feline awareness registry "
                    "contains invalid runtime state."
                )

        return tuple(
            self._records
        )


@dataclass(slots=True, frozen=True)
class FelineAbilityRegistryEntry:

    name: str
    ability: FelineAbilityState

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "name",
            str(
                self.name
            ),
        )

        if not isinstance(
            self.ability,
            FelineAbilityState,
        ):
            raise TypeError(
                "Feline ability registry entry "
                "requires FelineAbilityState."
            )


@dataclass(slots=True)
class FelineAbilityRegistry:

    _entries: list = field(
        default_factory=list
    )

    @property
    def is_empty(
        self,
    ):
        return not self._entries

    def store(
        self,
        ability_name,
        ability,
    ):
        if not isinstance(
            ability,
            FelineAbilityState,
        ):
            raise TypeError(
                "Feline ability registry requires "
                "FelineAbilityState."
            )

        ability_name = str(
            ability_name
        )

        entry = (
            FelineAbilityRegistryEntry(
                name=ability_name,
                ability=ability,
            )
        )

        for index, current in enumerate(
            self.entries()
        ):
            if current.name == ability_name:
                self._entries[
                    index
                ] = entry

                return ability

        self._entries.append(
            entry
        )

        return ability

    def remove(
        self,
        ability_name,
    ):
        ability_name = str(
            ability_name
        )

        for index, entry in enumerate(
            self.entries()
        ):
            if entry.name == ability_name:
                removed = self._entries.pop(
                    index
                )

                return removed.ability

        return None

    def record(
        self,
        ability_name,
    ):
        ability_name = str(
            ability_name
        )

        for entry in self.entries():
            if entry.name == ability_name:
                return entry.ability

        return None

    def records(
        self,
    ):
        return tuple(
            entry.ability
            for entry
            in self.entries()
        )

    def entries(
        self,
    ):
        for entry in self._entries:
            if not isinstance(
                entry,
                FelineAbilityRegistryEntry,
            ):
                raise TypeError(
                    "Feline ability registry "
                    "contains invalid runtime state."
                )

        return tuple(
            self._entries
        )
