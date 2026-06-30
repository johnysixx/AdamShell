from core.interaction.rule import Rule


class LightRule(Rule):

    def __init__(self):
        super().__init__(name="light", priority=10)

    def apply(self, universe, word):
        if word.name == "LetThereBeLight":
            return {
                "state": {
                    "light": True
                },
                "manifest": "Light",
                "birth_allowed": True
            }
        return None