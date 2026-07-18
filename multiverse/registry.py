class UniverseRegistry:

    def __init__(self):
        self.universes = {
            0: {
                "id": 0,
                "name": "multiverse",
                "type": "multiverse"
            },
            0.5: {
                "id": 0.5,
                "name": "quantum_layer",
                "type": "quantum_layer"
            }
        }

        self.ids_by_name = {
            "multiverse": 0,
            "quantum_layer": 0.5
        }

        self.next_universe_id = 1

    def register_universe(self, name, universe_type="universe"):
        if name in self.ids_by_name:
            return self.ids_by_name[name]

        universe_id = self.next_universe_id

        self.universes[universe_id] = {
            "id": universe_id,
            "name": name,
            "type": universe_type
        }

        self.ids_by_name[name] = universe_id
        self.next_universe_id += 1

        print(
            f"UNIVERSE REGISTERED: "
            f"{name} ID={universe_id}"
        )

        return universe_id
