from core.entity import factory
from core.word.voice import Voice
from core.word.words import LetThereBeLight
from core.genesis.day2 import LetThereBeSpace
from core.genesis.day3 import LetThereBeDeep
from core.word.chronicle import Chronicle
from universe import layerRegistry
from universe.universe import Universe
from core.observe.chronicle_viewer import ChronicleViewer
from core.observe.universe_probe import UniverseProbe
from core.entity.factory import EntityFactory
from eden import Eden
from meeting_place.meeting_place import MeetingPlace
from universe.layerRegistry import LayerRegistry
from library import Library
from root_universe import RootUniverse
from cats import Cats



class Bootstrap:

    def run(self):

        self.universe = Universe()
        self.universe.enable_quantum_layer()
        self.universe.boot_physics()

        self.god = {
            "name": "god",
            "type": "creator_entity",
            "state": "present",
            "active": True,
            "forbidden": False,

            "role": {
                "creator_of": ["eden"],
                "authority": "creator"
            },

            "access": {
                "eden": True,
                "universe": "via_eden",
                "quantum_layer": "via_eden",
                "meeting_place": True
            },

            "meeting_place_access": {
                "quantum_layer": True,
                "eden": False,
                "universe": False
            }
        }

        self.universe.create_entity("god")
        self.universe.world["god"] = self.god

        print("God entity created")

        self.cats = Cats(self.universe)

        self.pazuzu = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="green"
        )

        self.pazuzu["alias"] = "classical_probe_debug_entity"

        self.universe.create_entity("pazuzu")
        self.universe.world["pazuzu"] = self.pazuzu
        self.universe.world["classical_probe_debug_entity"] = self.pazuzu

        print("Pazuzu created as black cat")

        self.serpent = {
            "name": "serpent",
            "type": "primordial_entity",
            "state": "created",
            "active": False,
            "forbidden": False,

            "access": {
                "eden": True,
                "meeting_place": True,
                "quantum_layer": "via_meeting_place"
            },

            "serpent_process": {
                "ready": False,
                "active": False,
                "knowledge_payload": None,
                "target": None
            }
        }

        self.universe.create_entity("serpent")
        self.universe.world["serpent"] = self.serpent

        print("Serpent created")

        for _ in range(3):
            self.universe.tick_universe()

        self.universe.tick_universe()
        self.universe.tick_universe()

        self.layers = LayerRegistry()
        self.layers.register("root_universe", RootUniverse(self.universe))
        self.layers.register("eden", Eden(self.universe))
        self.layers.register("meeting", MeetingPlace(self.universe))
        self.layers.register("library", Library(self.universe))

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

        universe = Universe("root")
        chronicle = Chronicle()
        voice = Voice(universe, chronicle)
        factory = EntityFactory()
        universe.create_entity("test_entity")

        for _ in range(3):
            voice.speak(LetThereBeLight())
            universe.tick()
            universe.update_physics()

        for _ in range(3):
            voice.speak(LetThereBeSpace())
            universe.tick()
            universe.update_physics()

        for _ in range(3):
            voice.speak(LetThereBeDeep())
            universe.tick()
            universe.update_physics()

        print("\n--- CHRONICLE ---")

        # OBSERVE SYSTEM
        ChronicleViewer(chronicle).dump()
        UniverseProbe(universe).snapshot()
