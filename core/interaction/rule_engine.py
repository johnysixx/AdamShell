from core.interaction.rules.light import LightRule
from core.interaction.rules.space import SpaceRule
from core.interaction.rules.deep import DeepRule
from core.interaction.conflict import ConflictEngine
from core.entity.factory import EntityFactory


class RuleEngine:

    def __init__(self):
        self._rules = []
        self._conflict = ConflictEngine()
        self._factory = EntityFactory()
        self._load()

    def _load(self):
        self._rules.append(LightRule())
        self._rules.append(SpaceRule())
        self._rules.append(DeepRule())

    def apply(self, universe, word):

        effects = []

        for rule in sorted(self._rules, key=lambda r: r.priority, reverse=True):
            if rule.active:
                effects.append(rule.apply(universe, word))

        result, conflicts = self._conflict.resolve(effects)
        universe.register_conflicts(conflicts)

        if conflicts:
         print("\n⚔ Conflict Explanation:")

        for c in conflicts:
         print(
            f"- {c['key']} changed from {c['old']} → {c['new']}"
        )

        for c in conflicts:
            print(
            f"- {c['key']} changed from {c['old']} → {c['new']}"
        )

        if "state" in result:
            result = result["state"]

        for k, v in result.items():
            setattr(universe, k, v)
            print(f"{k} = {v}")

        return result, conflicts