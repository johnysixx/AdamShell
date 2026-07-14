class BarFridge:

    def __init__(self):
        self.name = "bar_fridge"
        self.type = "physical_bar_object"
        self.state = "closed"
        self.location = "behind_bar_counter_left"

        self.items = {
            "milk": {
                "name": "milk",
                "type": "bar_drink_ingredient",
                "form": "liquid",
                "state": "cold",
                "stored_in": "bar_fridge",
                "suitable_for": [
                    "cat",
                    "pazuzu",
                    "classical_probe_debug_entity"
                ]
            }
        }

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "location": self.location,
            "items": self.items
        }

        print("BAR FRIDGE CREATED")
        print("MILK STORED IN BAR FRIDGE")

    def get_item(self, item_name):
        return self.items.get(item_name)
    