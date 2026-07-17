class DiceBox:

    def __init__(self):
        self.name = "dice_box"
        self.type = "bar_object"
        self.location = "on_bar_counter"

        self.contents = [
            "d4",
            "d6",
            "d8",
            "d10",
            "d12",
            "d100"
        ]

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "contents": self.contents,
            "missing": ["d20"],
            "display_state": "closed_box_on_bar_counter",
            "visibility_scope": "inside_bar_only"
        }

        print("DICE BOX PLACED ON BAR COUNTER")

    def answer_about_contents(self):
        return "dice"

    def answer_about_d20(self):
        return "I do not know"
