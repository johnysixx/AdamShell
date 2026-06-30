from core.entity import factory
from core.word.voice import Voice
from core.word.words import LetThereBeLight
from core.genesis.day2 import LetThereBeSpace
from core.genesis.day3 import LetThereBeDeep
from core.word.chronicle import Chronicle
from universe.universe import Universe
from core.observe.chronicle_viewer import ChronicleViewer
from core.observe.universe_probe import UniverseProbe
from core.entity.factory import EntityFactory


class Bootstrap:

    def run(self):

        universe = Universe("root")
        chronicle = Chronicle()
        voice = Voice(universe, chronicle)
        factory = EntityFactory()
        universe.add_entity(factory.create("test_entity", universe))

        for _ in range(3):
            voice.speak(LetThereBeLight())
            universe.tick()

        for _ in range(3):
            voice.speak(LetThereBeSpace())
            universe.tick()

        for _ in range(3):
            voice.speak(LetThereBeDeep())
            universe.tick()


        print("\n--- CHRONICLE ---")

        # OBSERVE SYSTEM
        ChronicleViewer(chronicle).dump()
        UniverseProbe(universe).snapshot()