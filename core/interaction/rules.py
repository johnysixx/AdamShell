from core.interaction.rule import Rule


class LightRule(Rule):

    def __init__(self):
        super().__init__(name="light", priority=1)

    def apply(self, universe, word):
        if word.name == "LetThereBeLight":
            universe.light = True
            print("LightRule activated")


class SpaceRule(Rule):

    def __init__(self):
        super().__init__(name="space", priority=1)

    def apply(self, universe, word):
        if word.name == "LetThereBeSpace":
            universe.space = True
            universe.chaos = False
            universe.order = True
            print("SpaceRule activated")


class DeepRule(Rule):

    def __init__(self):
        super().__init__(name="deep", priority=1)

    def apply(self, universe, word):
        if word.name == "LetThereBeDeep":
            universe.deep = True
            print("DeepRule activated")


class RuleEngine:

    def __init__(self):
        self._rules = []
        self._load_default_rules()

    def _load_default_rules(self):
        self._rules.append(LightRule())
        self._rules.append(SpaceRule())
        self._rules.append(DeepRule())

    def apply(self, universe, word):

        for rule in sorted(self._rules, key=lambda r: r.priority, reverse=True):
            if rule.active:
                rule.apply(universe, word)

    def add_rule(self, rule):
        self._rules.append(rule)