from core.word.voice import Voice
from core.word.words import LetThereBeLight
from core.word.word_day2 import LetThereBeSpace
from core.word.chronicle import Chronicle
from universe.universe import Universe
from core.reality.divergence import DivergenceInjector


class Bootstrap:

    def run(self):

        universe = Universe()
        chronicle = Chronicle()
        voice = Voice(universe, chronicle)

        # DAY 1
        voice.speak(LetThereBeLight())

        # DAY 2
        voice.speak(LetThereBeSpace())

        print("\n--- STATE AFTER DAY 2 ---")
        print("Light:", universe.light)
        print("Space:", universe.space)
        print("Chaos:", universe.chaos)
        print("Order:", universe.order)