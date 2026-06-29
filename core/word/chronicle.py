from typing import List
from core.word.word import Word


class Chronicle:

    def __init__(self):
        self._words: List[Word] = []

    def record(self, word: Word):
        self._words.append(word)

    def all(self) -> List[Word]:
        return list(self._words)

    def replay(self, universe):
        """
        Rebuild universe state from scratch
        """
        for word in self._words:
            universe.hear(word)