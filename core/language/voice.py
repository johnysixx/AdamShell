class Voice:

    def __init__(self, chronicle):
        self._chronicle = chronicle
        self._witnesses = []

    def witness(self, witness):
        self._witnesses.append(witness)

    def speak(self, word):

        self._chronicle.write(word)

        for witness in self._witnesses:
            witness.hear(word)