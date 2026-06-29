class Entity:

    def __init__(self, name):

        self.name = name
        self.age = 0
        self.energy = 1
        self.state = "new"

    def tick(self):

        self.age += 1

        print(f"{self.name} -> age {self.age}")

    def describe(self):

        return f"{self.name} age={self.age} energy={self.energy}"