from core.word.voice import Voice
from core.word.words import LetThereBeLight
from core.word.chronicle import Chronicle
from universe.universe import Universe
from core.reality.divergence import DivergenceInjector


class Bootstrap:

    def run(self):

        # ORIGINAL REALITY
        universe = Universe()
        chronicle = Chronicle()
        voice = Voice(universe, chronicle)

        voice.speak(LetThereBeLight())

        print("\n--- INJECTING DIVERGENCE ---\n")

        injector = DivergenceInjector()

        # divergence: místo "LetThereBeLight" přidáme jinou realitu
        class LetThereBeDarkness:
            name = "LetThereBeDarkness"

        new_universe, new_chronicle = injector.inject(
            base_chronicle=chronicle,
            universe=universe,
            divergence_point=0,
            new_word=LetThereBeDarkness()
        )

        print("Original universe light:", universe.light)
        print("New universe light:", new_universe.light)
        chronicle.validate()