


class Entity:

    def __init__(self, name):

        self.name = name
        self.age = 0
        self.energy = 1
        self.state = "new"
        self.evolution_threshold = 5
        self.evolved = False
        self.birth_allowed = False
        self.depth = 0


    def tick(self, universe):

        self.age += 1

        self.react(universe)

        if not self.evolved and self.energy >= self.evolution_threshold:
            self.evolve(universe)

        print(f"{self.name} -> age {self.age}")
        print(f"DEBUG {self.name}: energy={self.energy}, age={self.age}")

    def describe(self):

        return f"{self.name} age={self.age} energy={self.energy}"

    def react(self, universe):

        if hasattr(universe, "light") and universe.light:
            self.energy += 1
            print(f"{self.name} -> energy {self.energy}")

    def evolve(self, universe):

        if self.energy < 5:
            return

        if self.depth >= 5:
            return

        if not hasattr(self, "birth_allowed") or not self.birth_allowed:
            return

        self.evolved = True
        self.state = "evolved"
        self.energy += 2

        print(f"🧬 {self.name} evolved → state={self.state}, energy={self.energy}")

        child_name = f"{self.name}_child_{self.age}"
        child = Entity(child_name)
        child.energy = self.energy // 2

        universe.add_entity(child)

        print(f"{self.name} spawned {child.name}")


    def is_alive(self):
        return self.energy > 0