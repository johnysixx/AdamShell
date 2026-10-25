from core.interaction.rule import Rule
from core.interaction.result_state import (
    InteractionEffectValue,
    InteractionRuleEffect,
)


class SpaceRule(Rule):

    def __init__(self):
        super().__init__(name="space", priority=8)

    def apply(self, universe, word):
        if word.name == "LetThereBeSpace":
            return InteractionRuleEffect(
                rule_name=self.name,
                effects=(
                    InteractionEffectValue(
                        "space",
                        True,
                    ),
                    InteractionEffectValue(
                        "chaos",
                        False,
                    ),
                    InteractionEffectValue(
                        "order",
                        True,
                    ),
                ),
            )
        return None