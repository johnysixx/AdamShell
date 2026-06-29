from core.interaction.rules import RuleEngine


class InteractionEngine:

    def __init__(self):
        self._rules = RuleEngine()

    def apply(self, universe, word):

        # delegace na RULE SYSTEM
        self._rules.apply(universe, word)