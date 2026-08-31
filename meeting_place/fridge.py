from universe.logger import UniverseLogger
from meeting_place.bar_objects import BarInventoryItem


class BarFridge:

    def __init__(self):
        self.name = "bar_fridge"
        self.type = "physical_bar_object"
        self.state = "closed"
        self.location = "behind_bar_counter_left"
        self.items = {
            "milk": BarInventoryItem(
                name="milk",
                type="bar_drink_ingredient",
                form="liquid",
                state="cold",
                stored_in="bar_fridge",
                suitable_for=[
                    "cat",
                    "pazuzu",
                    "classical_probe_debug_entity",
                ],
            )
        }
        UniverseLogger.boot("BAR FRIDGE CREATED")
        UniverseLogger.boot("MILK STORED IN BAR FRIDGE")

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "location": self.location,
            "items": {
                name: item.to_dict()
                for name, item in self.items.items()
            },
        }

    def get_item(self, item_name):
        return self.items.get(item_name)
