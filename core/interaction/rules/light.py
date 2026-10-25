from core.interaction.rule import Rule
from core.interaction.result_state import (
    InteractionEffectValue,
    InteractionRuleEffect,
)


class LightRule(Rule):

    def __init__(self):
        super().__init__(name="light", priority=10)

    def apply(self, universe, word):
        if word.name == "LetThereBeLight":
            return InteractionRuleEffect(
                rule_name=self.name,
                effects=(
                    InteractionEffectValue(
                        key="state",
                        value={"light": True},
                    ),
                    InteractionEffectValue(
                        key="manifest",
                        value="Light",
                    ),
                    InteractionEffectValue(
                        key="birth_allowed",
                        value=True,
                    ),
                ),
            )
        return None