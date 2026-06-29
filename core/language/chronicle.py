class Chronicle:

    def __init__(self):
        self._words = []

    def write(self, word):
        self._words.append(word)

    @property
    def words(self):
        return tuple(self._words)