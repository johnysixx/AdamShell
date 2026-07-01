from core.manifestation.manifestation import Manifestation


class LightManifestation(Manifestation):

    def __init__(self):
        super().__init__(name="Light")

    def apply(self, universe):
        universe.light = True
        print("🌟 Light manifested in the universe")