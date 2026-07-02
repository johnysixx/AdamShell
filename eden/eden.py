from typing import Self

from universe.universe import Universe


class Eden:

    def __init__(self, universe):
        self.universe = universe
        self.state = {
            "name": "eden",
            "type": "sandbox",
            "state": "initialized",
            "creator": "god",
            "created_by": "god",
            "administrator": "god",

            "permissions": {
                "can_administer": ["god"],
                "can_modify": ["god"]
            }
        }

        self.universe.world["eden"] = self.state

        print("EDEN CREATED BY: god")
        print("EDEN ADMINISTRATOR: god")

        self.entities = []

        self.plants = []
        self.trees = []
        self.animals = []
        self.rules = []
        self.observer = None
        self.relations = []

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

        grass =  {
            "name": "grass",
            "type": "plant",
            "state": "alive",
            "edible": True,
            "forbidden": False,
        }

        herb ={
            "name": "herb",
            "type": "plant",
            "state": "alive",
            "edible": True,
            "forbidden": False,
        }

        fruit_tree = {
            "name": "fruit_tree",
            "type": "tree",
            "state": "alive",
            "fruit": True,
            "forbidden": False,
        }

        self.plants.append(grass)
        self.plants.append(herb)
        self.trees.append(fruit_tree)

        self.entities.append(grass)
        self.entities.append(herb)
        self.entities.append(fruit_tree)

        self.universe.world["eden_plants"] = self.plants
        self.universe.world["eden_trees"] = self.trees
        self.universe.world["eden_entities"] = self.entities

        print("plants created: grass")
        print("plants created: herb")
        print("plants created: fruit_tree")


        self.universe.enable_physics("space")

    def day_2(self):
        print("DAY 2: ANIMALS")

        bird = {
            "name": "bird",
            "type": "animal",
            "kind": "air",
            "state": "alive",
            "forbidden": False
        }

        fish = {
            "name": "fish",
            "type": "animal",
            "kind": "water",
            "state": "alive",
            "forbidden": False
        }

        beast = {
            "name": "beast",
            "type": "animal",
            "kind": "land",
            "state": "alive",
            "forbidden": False
        }
        self.animals.append(bird)
        self.animals.append(fish)
        self.animals.append(beast)

        self.entities.append(bird)
        self.entities.append(fish)
        self.entities.append(beast)

        self.universe.world["eden_animals"] = self.animals
        self.universe.world["eden_entities"] = self.entities

        print("Animals created: bird")
        print("Animals created: fish")
        print("Animals created: beast")





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



