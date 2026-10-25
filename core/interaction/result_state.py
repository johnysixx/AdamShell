from copy import deepcopy
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class InteractionEffectValue:
    key: str
    value: object

    def __post_init__(self):
        object.__setattr__(self, "key", str(self.key))
        object.__setattr__(
            self, "value", deepcopy(self.value)
        )

    def to_dict(self):
        return {
            "key": self.key,
            "value": deepcopy(self.value),
        }


@dataclass(slots=True, frozen=True)
class InteractionRuleEffect:
    rule_name: str
    effects: tuple[InteractionEffectValue, ...]

    def __post_init__(self):
        object.__setattr__(
            self,
            "rule_name",
            str(self.rule_name),
        )

        effects = tuple(self.effects)

        if not all(
            isinstance(item, InteractionEffectValue)
            for item in effects
        ):
            raise TypeError(
                "Rule effects require "
                "InteractionEffectValue objects."
            )

        object.__setattr__(
            self,
            "effects",
            effects,
        )

    def to_dict(self):
        return {
            "rule_name": self.rule_name,
            "effects": [
                item.to_dict()
                for item in self.effects
            ],
        }


@dataclass(slots=True, frozen=True)
class InteractionConflictRecord:
    key: str
    old: object
    new: object
    strength: int = 1

    def __post_init__(self):
        object.__setattr__(self, "key", str(self.key))
        object.__setattr__(
            self, "old", deepcopy(self.old)
        )
        object.__setattr__(
            self, "new", deepcopy(self.new)
        )
        object.__setattr__(
            self, "strength", int(self.strength)
        )

    def to_dict(self):
        return {
            "key": self.key,
            "old": deepcopy(self.old),
            "new": deepcopy(self.new),
            "strength": self.strength,
        }


@dataclass(slots=True, frozen=True)
class InteractionConflictResolutionResult:
    effects: tuple[InteractionEffectValue, ...]
    conflicts: tuple[InteractionConflictRecord, ...]

    def __post_init__(self):
        effects = tuple(self.effects)
        conflicts = tuple(self.conflicts)

        if not all(
            isinstance(item, InteractionEffectValue)
            for item in effects
        ):
            raise TypeError(
                "Expected InteractionEffectValue objects."
            )

        if not all(
            isinstance(item, InteractionConflictRecord)
            for item in conflicts
        ):
            raise TypeError(
                "Expected InteractionConflictRecord objects."
            )

        object.__setattr__(self, "effects", effects)
        object.__setattr__(self, "conflicts", conflicts)

    def to_dict(self):
        return {
            "effects": {
                effect.key: deepcopy(effect.value)
                for effect in self.effects
            },
            "conflicts": [
                conflict.to_dict()
                for conflict in self.conflicts
            ],
        }
