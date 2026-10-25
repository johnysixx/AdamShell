from core.entity.factory import EntityFactory
from core.manifestation.light import LightManifestation
from core.interaction.result_state import (
    InteractionConflictResolutionResult,
)


class CreationEngine:

    def __init__(self):
        print("🔥 CREATION ENGINE LOADED")
        self._factory = EntityFactory()

    def apply(self, universe, resolution):
        if not isinstance(
            resolution,
            InteractionConflictResolutionResult,
        ):
            raise TypeError(
                "CreationEngine requires "
                "InteractionConflictResolutionResult."
            )

        birth_allowed = None
        manifest = None

        for effect in resolution.effects:
            if effect.key == "birth_allowed":
                birth_allowed = effect.value
            elif effect.key == "manifest":
                manifest = effect.value

        print("➡ CREATION ENGINE APPLY:", resolution)

        if birth_allowed is not None:
            for entity in universe.entities:
                entity.birth_allowed = birth_allowed

        print("BIRTH ALLOWED:", birth_allowed)



    # 2. MANIFESTATION
        print("MANIFEST VALUE:", manifest, type(manifest))

        if manifest is not None and manifest == "Light":
            print("LIGHT MATCHED")
            LightManifestation().apply(universe)