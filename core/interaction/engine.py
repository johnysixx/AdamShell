from core.interaction.rule_engine import RuleEngine


class InteractionEngine:

    def __init__(self):
        self._rules = RuleEngine()

    def apply(self, universe, word):
        return self._rules.apply(universe, word)