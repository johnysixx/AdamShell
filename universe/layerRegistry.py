class LayerRegistry:

    def __init__(self):
        self.layers = {}

        print(LayerRegistry)

    def register(self, name, layer):
        self.layers[name] = layer
        print(f"🧩 Layer registered: {name}")


    def get(self, name):
        return self.layers.get(name)