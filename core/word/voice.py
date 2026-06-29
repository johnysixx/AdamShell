from core.interaction.engine import InteractionEngine


class Voice:

    def __init__(self, witness, chronicle):
        self._witness = witness
        self._chronicle = chronicle
        self._engine = InteractionEngine()

    def speak(self, word):

        # 1. uložit do historie
        self._chronicle.record(word)

        # 2. INTERACTION LAYER (nově)
        self._engine.apply(self._witness, word)