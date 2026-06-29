from core.interaction.rule import Rule


class SpaceRule(Rule):

    def __init__(self):
        super().__init__(name="space", priority=8)

    def apply(self, universe, word):
        if word.name == "LetThereBeSpace":
            return {"space": True, "chaos": False, "order": True}
        return None