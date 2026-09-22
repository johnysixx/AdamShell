from eden.creation_objects import (
    CreationDarkness,
    CreationDayPhase,
    CreationDayRecord,
    CreationLight,
)
from eden.eden_state import EdenState
from eden.living_objects import EdenAnimal, EdenFruitTree, EdenPlant
from universe.logger import UniverseLogger


class Eden:

    def __init__(self, universe):
        self.universe = universe
        self.eden_state = EdenState()
        self.state = self.eden_state

        self.write_to_world()

        UniverseLogger.boot("EDEN CREATED BY: god")
        UniverseLogger.boot("EDEN ADMINISTRATOR: god")

        UniverseLogger.boot("EDEN INITIALIZED")

    @property
    def entities(self):
        return self.eden_state.entities

    @entities.setter
    def entities(self, value):
        self.eden_state.entities = value

    @property
    def plants(self):
        return self.eden_state.plants

    @plants.setter
    def plants(self, value):
        self.eden_state.plants = value

    @property
    def trees(self):
        return self.eden_state.trees

    @trees.setter
    def trees(self, value):
        self.eden_state.trees = value

    @property
    def animals(self):
        return self.eden_state.animals

    @animals.setter
    def animals(self, value):
        self.eden_state.animals = value

    @property
    def rules(self):
        return self.eden_state.rules

    @rules.setter
    def rules(self, value):
        self.eden_state.rules = value

    @property
    def observer(self):
        return self.eden_state.observer

    @observer.setter
    def observer(self, value):
        self.eden_state.observer = value

    @property
    def relations(self):
        return self.eden_state.relations

    @relations.setter
    def relations(self, value):
        self.eden_state.relations = value

    @property
    def day(self):
        return self.eden_state.day

    @day.setter
    def day(self, value):
        self.eden_state.day = value

    @property
    def max_day(self):
        return self.eden_state.max_day

    @max_day.setter
    def max_day(self, value):
        self.eden_state.max_day = value

    @property
    def tick_count(self):
        return self.eden_state.tick_count

    @tick_count.setter
    def tick_count(self, value):
        self.eden_state.tick_count = value

    @property
    def permissions(self):
        return self.eden_state.permissions

    @permissions.setter
    def permissions(self, value):
        self.eden_state.permissions = value

    @property
    def public_state(self):
        return {
            "name": self.eden_state.name,
            "type": self.eden_state.layer_type,
            "state": self.eden_state.status,
            "creator": self.eden_state.creator,
            "created_by": self.eden_state.created_by,
            "administrator": self.eden_state.administrator,
            "permissions": self.permissions,
            "eden_state": self.eden_state.to_dict(),
        }

    def write_to_world(self):
        self.universe.world["eden"] = self.public_state
        self.universe.world["eden_state"] = self.eden_state

    def add_entity(self, entity):
        self.entities.append(entity)
        self.write_to_world()

    def tick(self):

        self.tick_count += 1

        UniverseLogger.event(f"EDEN DAY {self.day}")

        handler = getattr(self, f"day_{self.day}", None)
        if handler:
            handler()

        self.day += 1

        self.universe.tick_time()

        self.write_to_world()

        UniverseLogger.event(f"EDEN DAY {self.day} | TIME {self.universe.get_time()} | ENERGY {self.universe.get_energy():.2f}")

    def day_0(self):
        UniverseLogger.event("day 0: start")
        UniverseLogger.event("DAY 0: PHYSICS")

        self.universe.enable_physics("light")
        self.universe.enable_physics("time")
        self.universe.enable_physics("gravity")
        self.universe.enable_physics("space")
        self.universe.enable_physics("energy")

        light = CreationLight()
        self.universe.world["light"] = light

        self.universe.world["time"] = (
            self.universe.physics["time"]
        )

        self.universe.physics["time_dilation"] = True

        UniverseLogger.event("EDEN PHYSICS ESTABLISHED")

        UniverseLogger.event("God separated the light from the darkness")
        light.name_as_day()

        self.universe.physics["darkness"] = CreationDarkness()

        UniverseLogger.event("God called the darkness night")

        light.mark_good()
        UniverseLogger.event("God saw that the light was good")

        self.universe.world["evening"] = CreationDayPhase(
            day=0,
            state="evening",
        )
        UniverseLogger.event("And there was evening")
        self.universe.world["morning"] = CreationDayPhase(
            day=0,
            state="morning",
        )

        UniverseLogger.event("And there was morning")
        self.universe.world["creation_day"] = CreationDayRecord(
            day=0,
            name="first day of the creation",
            complete=True,
        )
        UniverseLogger.event("and the first day on the Earth begins")


        UniverseLogger.event(f"LIGHT= {self.universe.physics['light']}")
        UniverseLogger.event(f"DARKNESS= {self.universe.physics['darkness']}")





    def day_1(self):
        UniverseLogger.event("DAY 1: PLANTS")

        grass = EdenPlant(name="grass")
        herb = EdenPlant(name="herb")
        fruit_tree = EdenFruitTree()

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

        bird = EdenAnimal(
            name="bird",
            kind="air",
        )
        fish = EdenAnimal(
            name="fish",
            kind="water",
        )
        beast = EdenAnimal(
            name="beast",
            kind="land",
        )
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


