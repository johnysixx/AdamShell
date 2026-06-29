from core.interaction.rule import Rule


class DeepRule(Rule):

    def __init__(self):
        super().__init__(name="deep", priority=5)

    def apply(self, universe, word):
        if word.name == "LetThereBeDeep":
            return {"deep": True}
        return None