class ChronicleViewer:

    def __init__(self, chronicle):
        self._chronicle = chronicle

    def dump(self):
        print("\n--- CHRONICLE ---")
        for i, word in enumerate(self._chronicle.all()):
            print(f"{i}: {word.name}")