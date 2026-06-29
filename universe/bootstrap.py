from core.word.voice import Voice
from core.word.words import LetThereBeLight
from core.word.chronicle import Chronicle
from universe.universe import Universe
from core.reality.fork import Fork


class Bootstrap:

    def run(self):

        # ORIGINAL UNIVERSE
        universe = Universe()
        chronicle = Chronicle()
        voice = Voice(universe, chronicle)

        voice.speak(LetThereBeLight())

        print("\n--- FORKING REALITY ---\n")

        fork = Fork()
        new_universe, timeline = fork.create(chronicle, universe)

        print(f"New universe: {new_universe.id}")
        print(f"Timeline: {timeline.id}")