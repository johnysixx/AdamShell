from core.interaction.rule import Rule
from core.interaction.rules import LightRule, SpaceRule, DeepRule, ConflictEngine


class LightRule(Rule):

    def __init__(self):
        super().__init__(name="light", priority=10)

    def apply(self, universe, word):

        if word.name == "LetThereBeLight":
            return {"light": True, "chaos_reduction": 0.2}

        return None


class SpaceRule(Rule):

    def __init__(self):
        super().__init__(name="space", priority=8)

    def apply(self, universe, word):

        if word.name == "LetThereBeSpace":
            return {"space": True, "order": True}

        return None

class DeepRule(Rule):

    def __init__(self):
        super().__init__(name="deep", priority=5)

    def apply(self, universe, word):

        if word.name == "LetThereBeDeep":
            return {"deep": True, "chaos": True}

        return None

class RuleEngine:

    def __init__(self):
        self._rules = []
        self._conflict = ConflictEngine()
        self._load_default_rules()

    def _load_default_rules(self):
        self._rules.append(LightRule())
        self._rules.append(SpaceRule())
        self._rules.append(DeepRule())

    def apply(self, universe, word):

        effects = []

        # 1. sběr efektů
        for rule in sorted(self._rules, key=lambda r: r.priority, reverse=True):
            if rule.active:
                effects.append(rule.apply(universe, word))

        # 2. konflikt resolution
        result = self._conflict.resolve(effects)

        # 3. aplikace výsledku do Universe
        for key, value in result.items():
            setattr(universe, key, value)

            print(f"Conflict resolved → {key} = {value}")

class ConflictEngine:

    def resolve(self, effects):

        """
        effects = list of dicts from rules
        """

        final_state = {}

        for effect in effects:

            if not effect:
                continue

            for key, value in effect.items():

                # pokud už existuje, konflikt řeší PRIORITA (implicitně poslední wins)
                final_state[key] = value

        return final_state