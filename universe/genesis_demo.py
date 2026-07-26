from core.entity.factory import EntityFactory
from core.genesis.day2 import LetThereBeSpace
from core.genesis.day3 import LetThereBeDeep
from core.observe.chronicle_viewer import ChronicleViewer
from core.observe.universe_probe import UniverseProbe
from core.word.chronicle import Chronicle
from core.word.voice import Voice
from core.word.words import LetThereBeLight
from universe.universe import Universe


class GenesisDemo:

    def run(self):
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

        ChronicleViewer(chronicle).dump()
        UniverseProbe(universe).snapshot()
