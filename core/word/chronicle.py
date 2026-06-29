from typing import List
from core.word.word import Word


class Chronicle:

    def __init__(self):
        self._words: List[Word] = []

    def record(self, word: Word):
        self._words.append(word)

    def all(self) -> List[Word]:
        return list(self._words)

    def last(self) -> Word | None:
        return self._words[-1] if self._words else None