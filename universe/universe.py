import uuid
from core.word.word import Word


class Universe:

    def __init__(self, universe_id=None):
        self.id = universe_id or str(uuid.uuid4())

        self.light = False
        self.space = False
        self.life = False

        print(f"Universe created: {self.id}")
        print("The universe exists.")

    def hear(self, word):

        if not hasattr(word, "name"):
            raise ValueError("Invalid Word received")

        if word.name == "LetThereBeLight":
            self.light = True

        else:
            # default safe behavior
            pass