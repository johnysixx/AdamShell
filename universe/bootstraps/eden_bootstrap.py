from eden import Eden


class EdenBootstrap:

    EDEN_INFLUENCES = {
        0: {
            "event": "physics_established",
            "effect": "root_universe_receives_initial_physics_imprint"
        },
        1: {
            "event": "plants_created",
            "effect": "root_universe_receives_life_and_growth_imprint"
        },
        2: {
            "event": "animals_created",
            "effect": "root_universe_receives_movement_instinct_and_living_creatures_imprint"
        }
    }

    def __init__(self, universe, layers):
        self.universe = universe
        self.layers = layers

    def run(self):
        eden = Eden(self.universe)
        root_universe = self.layers.get("root_universe")

        self.layers.register("eden", eden)

        for day in range(8):
            eden.tick()

            influence = self.EDEN_INFLUENCES.get(day)
            if influence:
                root_universe.apply_eden_influence(
                    "god",
                    {
                        "source": "eden",
                        "day": day,
                        **influence
                    }
                )

        self.layers.get("meeting").tick()
