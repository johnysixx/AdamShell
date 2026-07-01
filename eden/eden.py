from typing import Self

from universe.universe import Universe


class Eden:

    def __init__(self, universe):
        self.universe = universe
        self.entities = []
        self.day = 0
        self.max_day =7
        self.tick_count = 0

        print("🌱 EDEN INITIALIZED")

    def add_entity(self, entity):
        self.entities.append(entity)

    def tick(self):

        self.tick_count += 1

        print(f"EDEN DAY {self.day}")

        handler = getattr(self, f"day_{self.day}", None)
        if handler:
            handler()

        self.day += 1

        self.universe.tick_time()

        print(
            f"EDEN DAY {self.day} | TIME {self.universe.get_time()} | ENERGY {self.universe.get_energy():.2f}"
        )

    def day_0(self):
        print("day 0: start")
        print("DAY 0: PHYSICS")

        self.universe.enable_physics("light")
        self.universe.enable_physics("time")
        self.universe.enable_physics("gravity")
        self.universe.enable_physics("space")
        self.universe.enable_physics("energy")

        self.universe.world["light"] = {
        "intensity": 1.0,
        "state": "primordial",
        "speed": 299792458,
        "constant": True
        }

        self.universe.world["time"] = {
            "tick": 0,
            "flow": 1.0,
            "state": "linear"
        }

        self.universe.physics["time_dilation"] = True

        print(self.universe.world)

        print("God separated the light from the darkness")
        self.universe.world["light"]["name"] = "day"

        self.universe.physics["darkness"] = {
            "name": "night",
            "state": "primordial"
        }

        print("God called the darkness night")

        self.universe.world["light"]["good"] = True
        print("God saw that the light was good")

        self.universe.world["evening"] =  {
            "day": 0,
            "state": "evening"
        }
        print("And there was evening")
        self.universe.world["morning"] = {
            "day": 0,
            "state": "morning"
        }

        print("And there was morning")
        self.universe.world["creation_day"] = {
            "day": 0,
            "name":"first day of the creation",
            "complete": True
        }
        print("and the first day on the Earth begins")


        print(self.universe.physics["light"])
        print("DARKNESS= ", self.universe.physics["darkness"])





    def day_1(self):
        print("DAY 1: PLANTS")
        self.universe.enable_physics("space")

    def day_2(self):
        print("DAY 2: ANIMALS")

    def day_3(self):
        print("DAY 3: TREE OF KNOWLEDGE")

    def day_4(self):
        print("DAY 4: ADAM")

    def day_5(self):
        print("DAY 5: EVA")

    def day_6(self):
        print("DAY 6: conflict")

    def day_7(self):
        print("sedmeho dne buh odpocival")

    def get_time(self):
        return self.universe.physics["time"]["tick"]



