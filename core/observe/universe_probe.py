class UniverseProbe:

    def __init__(self, universe):
        self._universe = universe

    def snapshot(self):
        print("\n--- UNIVERSE SNAPSHOT ---")
        print("light:", self._universe.light)
        print("space:", self._universe.space)
        print("chaos:", self._universe.chaos)
        print("order:", self._universe.order)