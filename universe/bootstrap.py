from core.word.voice import Voice
from core.word.words import LetThereBeLight
from core.word.chronicle import Chronicle
from universe.universe import Universe


class Bootstrap:

    def run(self):

        universe = Universe()
        chronicle = Chronicle()

        voice = Voice(universe, chronicle)

        voice.speak(LetThereBeLight())