from typing import Self

from universe.universe import Universe
from universe.logger import UniverseLogger


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

        UniverseLogger.boot("EDEN CREATED BY: god")
        UniverseLogger.boot("EDEN ADMINISTRATOR: god")

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

        UniverseLogger.boot("EDEN INITIALIZED")

    def add_entity(self, entity):
        self.entities.append(entity)

    def tick(self):

        self.tick_count += 1

        UniverseLogger.event(f"EDEN DAY {self.day}")

        handler = getattr(self, f"day_{self.day}", None)
        if handler:
            handler()

        self.day += 1

        self.universe.tick_time()

        UniverseLogger.event(f"EDEN DAY {self.day} | TIME {self.universe.get_time()} | ENERGY {self.universe.get_energy():.2f}")

    def day_0(self):
        UniverseLogger.event("day 0: start")
        UniverseLogger.event("DAY 0: PHYSICS")

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

        UniverseLogger.event("EDEN PHYSICS ESTABLISHED")

        UniverseLogger.event("God separated the light from the darkness")
        self.universe.world["light"]["name"] = "day"

        self.universe.physics["darkness"] = {
            "name": "night",
            "state": "primordial"
        }

        UniverseLogger.event("God called the darkness night")

        self.universe.world["light"]["good"] = True
        UniverseLogger.event("God saw that the light was good")

        self.universe.world["evening"] =  {
            "day": 0,
            "state": "evening"
        }
        UniverseLogger.event("And there was evening")
        self.universe.world["morning"] = {
            "day": 0,
            "state": "morning"
        }

        UniverseLogger.event("And there was morning")
        self.universe.world["creation_day"] = {
            "day": 0,
            "name":"first day of the creation",
            "complete": True
        }
        UniverseLogger.event("and the first day on the Earth begins")


        UniverseLogger.event(f"LIGHT= {self.universe.physics['light']}")
        UniverseLogger.event(f"DARKNESS= {self.universe.physics['darkness']}")





    def day_1(self):
        UniverseLogger.event("DAY 1: PLANTS")

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

        UniverseLogger.event("plants created: grass")
        UniverseLogger.event("plants created: herb")
        UniverseLogger.event("plants created: fruit_tree")



    def day_2(self):
        UniverseLogger.event("DAY 2: ANIMALS")

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

        UniverseLogger.event("Animals created: bird")
        UniverseLogger.event("Animals created: fish")
        UniverseLogger.event("Animals created: beast")





    def day_3(self):
        UniverseLogger.event("DAY 3: TREE OF KNOWLEDGE")

    def day_4(self):
        UniverseLogger.event("DAY 4: ADAM")

    def day_5(self):
        UniverseLogger.event("DAY 5: EVA")

    def day_6(self):
        UniverseLogger.event("DAY 6: conflict")

    def day_7(self):
        UniverseLogger.event("sedmeho dne buh odpocival")

    def get_time(self):
        return self.universe.physics["time"].tick



