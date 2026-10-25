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

        resolution = self._conflict.resolve(effects)
        universe.register_conflicts(resolution.conflicts)

        if resolution.conflicts:
            print("\nConflict Explanation:")
            for conflict in resolution.conflicts:
                print(
                    f"- {conflict.key} changed from "
                    f"{conflict.old} -> {conflict.new}"
                )

        creation_payload = resolution.to_dict()["effects"]
        creation_payload.setdefault("state", {})

        self._creation.apply(universe, creation_payload)

        return resolution