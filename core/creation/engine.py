from core.entity.factory import EntityFactory
from core.manifestation.light import LightManifestation


class CreationEngine:

    def __init__(self):
        print("🔥 CREATION ENGINE LOADED")
        self._factory = EntityFactory()

    def apply(self, universe, effects):

        print("➡ CREATION ENGINE APPLY:", effects)

        birth_allowed = effects.get("birth_allowed", None)

        if birth_allowed is not None:
            for entity in universe.entities:
                entity.birth_allowed = birth_allowed

        print("BIRTH ALLOWED:", birth_allowed)



    # 2. MANIFESTATION
        manifest = effects.get("manifest", None)

        print("MANIFEST VALUE:", manifest, type(manifest))

        if manifest is not None and manifest == "Light":
            print("LIGHT MATCHED")
            LightManifestation().apply(universe)