class Universe:

    def __init__(self, universe_id=None):
        self.id = universe_id or "root"

        self.light = False
        self.space = False

        self.chaos = True
        self.order = False

        print(f"Universe created: {self.id}")
        print("The universe exists.")

    def hear(self, word):

        if word.name == "LetThereBeLight":
            self.light = True
            print("Light is created.")

        elif word.name == "LetThereBeSpace":
            self.space = True
            self.chaos = False
            self.order = True
            print("Space is separated from chaos.")