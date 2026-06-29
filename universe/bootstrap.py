from core.word.voice import Voice
from core.word.words import LetThereBeLight
from core.word.chronicle import Chronicle
from universe.universe import Universe
from core.reality.fork import Fork
from core.reality.compare import RealityComparison


class Bootstrap:

    def run(self):

        # REALITY A
        universe_a = Universe()
        chronicle_a = Chronicle()
        voice_a = Voice(universe_a, chronicle_a)

        voice_a.speak(LetThereBeLight())

        # FORK → REALITY B
        fork = Fork()
        universe_b, timeline = fork.create(chronicle_a, universe_a)

        chronicle_b = Chronicle()
        voice_b = Voice(universe_b, chronicle_b)

        # divergence: B má jiné Slovo
        print("\n--- DIVERGENCE ---\n")

        # A pokračuje jinak než B
        # (B zatím NIC nepřidá → čistá divergence)

        # COMPARE
        comparison = RealityComparison()

        diff = comparison.compare(chronicle_a, chronicle_b)

        print("Differences:")
        for d in diff:
            print(d)