class Chronicle:

    def __init__(self):
        self._words = []

    def record(self, word):
        if word is None:
            raise ValueError("Word cannot be None")

        self._words.append(word)

    def all(self):
        return tuple(self._words)  # IMMUTABILITY guarantee

    def replay(self, universe):
        for word in self._words:
            universe.hear(word)

    def validate(self):
        """
        Ensures chronicle consistency
        """
        for w in self._words:
            if not hasattr(w, "name"):
                raise ValueError(f"Invalid Word detected: {w}")