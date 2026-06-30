from core.creation.engine import CreationEngine
from core.interaction.rules.light import LightRule
from core.interaction.rules.space import SpaceRule
from core.interaction.rules.deep import DeepRule
from core.interaction.conflict import ConflictEngine
from core.entity.factory import EntityFactory


class RuleEngine:

    def __init__(self):
        print("RULE ENGINE INIT")

        self._rules = []
        self._conflict = ConflictEngine()
        self._factory = EntityFactory()
        self._creation = CreationEngine()


        print("CREATION ENGINE INSTANCE:", self._creation)

        self._load()


    def _load(self):
        self._rules.append(LightRule())
        self._rules.append(SpaceRule())
        self._rules.append(DeepRule())

    def apply(self, universe, word):

        effects = []

        for rule in sorted(self._rules, key=lambda r: r.priority, reverse=True):
            if rule.active:
                effect = rule.apply(universe, word)
                if effect is not None:
                    effects.append(effect)

        result, conflicts = self._conflict.resolve(effects)
        universe.register_conflicts(conflicts)

        if conflicts:
            print("\n⚔ Conflict Explanation:")
            for c in conflicts:
                print(f"- {c['key']} changed from {c['old']} → {c['new']}")

        state = result.get("state", {})

        clean_result = dict(result)
        clean_result["state"] = state

        self._creation.apply(universe, clean_result)

        return clean_result, conflicts