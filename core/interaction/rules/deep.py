from core.interaction.rule import Rule
from core.interaction.result_state import (
    InteractionEffectValue,
    InteractionRuleEffect,
)


class DeepRule(Rule):

    def __init__(self):
        super().__init__(name="deep", priority=5)

    def apply(self, universe, word):
        if word.name == "LetThereBeDeep":
            return InteractionRuleEffect(
                rule_name=self.name,
                effects=(
                    InteractionEffectValue(
                        "deep",
                        True,
                    ),
                ),
            )
        return None