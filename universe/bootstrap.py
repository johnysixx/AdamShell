from core.word.voice import Voice
from core.word.words import LetThereBeLight
from core.genesis.day2 import LetThereBeSpace
from core.genesis.day3 import LetThereBeDeep
from core.word.chronicle import Chronicle
from universe.universe import Universe
from core.observe.chronicle_viewer import ChronicleViewer
from core.observe.universe_probe import UniverseProbe
from core.entity.entity import Entity


class Bootstrap:

    def run(self):

        universe = Universe("root")
        chronicle = Chronicle()
        voice = Voice(universe, chronicle)
        universe.add_entity(Entity("test_entity"))

        # DAY 1
        voice.speak(LetThereBeLight())

        # DAY 2
        voice.speak(LetThereBeSpace())

        # DAY 3
        voice.speak(LetThereBeDeep())

        universe.tick()
        print("\n--- CHRONICLE ---")

        # OBSERVE SYSTEM
        ChronicleViewer(chronicle).dump()
        UniverseProbe(universe).snapshot()