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


class Bootstrap:

    def run(self):

        self.universe = Universe()
        self.universe.boot_physics()

        self.layers = LayerRegistry()
        self.layers.register("eden", Eden(self.universe))
        self.layers.register("meeting", MeetingPlace(self.universe))
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