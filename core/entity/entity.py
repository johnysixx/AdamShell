from core.entities.ability_set import AbilitySet


class Entity:

    def __init__(self, name):

        self.name = name
        self.age = 0
        self.energy = 1
        self.state = "new"
        self.evolution_threshold = 5
        self.evolved = False
        self.depth = 0
        self.birth_allowed = False

        self.abilities = AbilitySet(
            owner=self
        )


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
            self.energy -= universe.pressure * 0.1

        if universe.energy_pool > 0:
            transfer = 0.05
            self.energy += transfer
            universe.energy_pool -= transfer
            print(f"{self.name} -> energy {self.energy}")

    def evolve(self, universe, parent=None):

        if self.energy < 5:
            return

        if self.depth >= 5:
            return

        if not (self, "birth_allowed") or not self.birth_allowed:
            return

        if universe.energy_pool  < 10:
            return

        self.evolved = True
        self.state = "evolved"
        self.energy += 2

        print(f"🧬 {self.name} evolved → state={self.state}, energy={self.energy}")

        child_name = f"{self.name}_child_{self.age}"
        child = Entity(child_name)

        child.energy = self.energy  // 2
        child.depth = self.depth + 1

        universe.add_entity(child)

        print(f"{self.name} spawned {child.name}")


    def is_alive(self):
        return self.energy > 0