from unicodedata import name


class UniverseProbe:

    def __init__(self, universe):
        self._universe = universe

    def snapshot(self):

        print("\n--- UNIVERSE SNAPSHOT (ENTITY MODE) ---")

        if not self._universe.entities:
            print("No entities found.")

        else:
            for e in self._universe.entities:
                name = getattr(e, "name", "unknown")
                age = getattr(e, "age", 0)
                print(f"{name}: {age}")
