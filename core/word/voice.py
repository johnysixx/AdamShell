class Voice:

    def __init__(self, witness, chronicle):
        self._witness = witness
        self._chronicle = chronicle

    def speak(self, word):

        # 1. uložit do historie
        self._chronicle.record(word)

        # 2. doručit světu
        self._witness.hear(word)