from core.word.word import Word


class Universe:

    def __init__(self):
        self.light = False
        self.space = False
        self.life = False

        print("Universe created.")
        print("The universe exists.")

    def hear(self, word: Word):

        if word.name == "LetThereBeLight":
            self.light = True
            print("Light is created.")