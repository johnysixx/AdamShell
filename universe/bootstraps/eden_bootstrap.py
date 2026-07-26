from eden import Eden
from universe.genesis_demo import GenesisDemo


class EdenBootstrap:

    def __init__(self, universe, layers):
        self.universe = universe
        self.layers = layers

    def run(self):
        self.layers.register("eden", Eden(self.universe))

        self.layers.get("eden").tick()

        self.layers.get("root_universe").apply_eden_influence(
            "god",
            {
                "source": "eden",
                "day": 0,
                "event": "physics_established",
                "effect": "root_universe_receives_initial_physics_imprint"
            }
        )

        self.layers.get("eden").tick()

        self.layers.get("root_universe").apply_eden_influence(
            "god",
            {
                "source": "eden",
                "day": 1,
                "event": "plants_created",
                "effect": "root_universe_receives_life_and_growth_imprint"
            }
        )

        self.layers.get("eden").tick()

        self.layers.get("root_universe").apply_eden_influence(
            "god",
            {
                "source": "eden",
                "day": 2,
                "event": "animals_created",
                "effect": "root_universe_receives_movement_instinct_and_living_creatures_imprint"
            }
        )

        self.layers.get("eden").tick()
        self.layers.get("meeting").tick()

        GenesisDemo().run()
