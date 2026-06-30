from universe.universe import Universe


class Eden:

    def __init__(self, universe):
        self.universe = Universe("eden")
        self.entities = []
        self.tick_count = 0

        print("🌱 EDEN INITIALIZED")

    def add_entity(self, entity):
        self.entities.append(entity)

    def tick(self):
        self.universe.tick()
        print(f"🌿 EDEN tick {self.tick_count}")