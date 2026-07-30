from universe.logger import UniverseLogger

class LayerRegistry:

    def __init__(self):
        self.layers = {}

        UniverseLogger.boot("LayerRegistry initialized")

    def register(self, name, layer):
        self.layers[name] = layer
        UniverseLogger.boot(f"Layer registered: {name}")


    def get(self, name):
        return self.layers.get(name)
