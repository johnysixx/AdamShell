from copy import deepcopy

from core.interaction.result_state import (
    InteractionConflictRecord,
    InteractionConflictResolutionResult,
    InteractionEffectValue,
    InteractionRuleEffect,
)


class ConflictEngine:

    def resolve(self, effects):
        resolved = {}
        conflicts = []

        for effect in effects:
            if effect is None:
                continue

            if not isinstance(
                effect,
                InteractionRuleEffect,
            ):
                raise TypeError(
                    "ConflictEngine requires "
                    "InteractionRuleEffect objects."
                )

            for item in effect.effects:
                key = item.key
                value = item.value
                if key in resolved and resolved[key] != value:
                    conflicts.append(
                        InteractionConflictRecord(
                            key=key,
                            old=resolved[key],
                            new=value,
                            strength=1,
                        )
                    )

                resolved[key] = deepcopy(value)

        return InteractionConflictResolutionResult(
            effects=tuple(
                InteractionEffectValue(
                    key=key,
                    value=value,
                )
                for key, value in resolved.items()
            ),
            conflicts=tuple(conflicts),
        )
