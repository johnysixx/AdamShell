from core.word.word import Word


class DivergencePoint:

    def __init__(self, index: int, note: str = ""):
        self.index = index
        self.note = note

from core.word.word import Word
from core.reality.timeline import Timeline
from universe.universe import Universe
from core.word.chronicle import Chronicle

class DivergenceInjector:

    def inject(self, base_chronicle, universe, divergence_point, new_word):

        words = base_chronicle.all()

        if divergence_point < 0 or divergence_point > len(words):
            raise ValueError("Invalid divergence point")

        new_chronicle = Chronicle()

        for i, word in enumerate(words):
            if i == divergence_point:
                new_chronicle.record(new_word)
                break
            new_chronicle.record(word)

        new_universe = Universe(universe_id=f"{universe.id}-div")

        new_chronicle.replay(new_universe)

        return new_universe, new_chronicle