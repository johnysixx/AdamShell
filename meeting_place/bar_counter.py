from universe.logger import UniverseLogger

class BarStoryBook:

    def __init__(self):
        self.name = "bar_story_book"
        self.type = "hidden_story_book"
        self.location = "under_bar_counter"
        self.entries = []

        UniverseLogger.boot("BAR STORY BOOK CREATED")

    def write_entry(self, event):
        self.entries.append(event)
        print(f"BAR STORY BOOK ENTRY: {event}")

    def read_entries(self):
        return self.entries


from .red_button import RedButton


class BarCounter:

    def __init__(self):
        self.name = "bar_counter"
        self.type = "bar_furniture"
        self.state = "created"

        UniverseLogger.boot("BAR COUNTER CREATED")

        self.hidden_story_book = BarStoryBook()

        self.bar_cloth = {
            "name": "bar_cloth",
            "type": "bar_tool",
            "location": "under_bar_counter",
            "visible_use": "wiping_bar"
        }

        UniverseLogger.boot("BAR CLOTH PLACED UNDER BAR COUNTER")

        self.red_button = RedButton()

        self.milk_bowl = {
            "name": "milk_bowl",
            "type": "bar_serving_object",
            "state": "empty",
            "location": "under_bar_counter_next_to_bar_cloth",
            "intended_use": "serving_milk_to_cats"
        }

        UniverseLogger.boot("MILK BOWL PLACED UNDER BAR COUNTER NEXT TO BAR CLOTH")

    def write_bar_story(self, event):
        self.hidden_story_book.write_entry(event)

    def read_bar_stories(self):
        return self.hidden_story_book.read_entries()


    def attach_menu_sign(
        self,
        menu_sign
    ):
        self.menu_sign = menu_sign

        UniverseLogger.boot(
            "BAR MENU SIGN CONNECTED TO BAR COUNTER"
        )

    def tap_menu(
        self,
        target=None
    ):
        if not hasattr(
            self,
            "menu_sign"
        ):
            raise RuntimeError(
                "Bar counter has no menu sign."
            )

        if target is None:
            UniverseLogger.event(
                "BAR COUNTER MENU OPEN TAP"
            )

            return self.menu_sign.open()

        if target == "back":
            return self.tap_menu_back()

        try:
            return self.tap_menu_drink(
                target
            )
        except ValueError:
            UniverseLogger.event(
                "BAR COUNTER MENU TAP IGNORED: "
                f"{target}"
            )

            return False
    def tap_menu_drink(
        self,
        drink
    ):
        if not hasattr(
            self,
            "menu_sign"
        ):
            raise RuntimeError(
                "Bar counter has no menu sign."
            )

        UniverseLogger.event(
            "BAR COUNTER MENU TAP: "
            f"{drink}"
        )

        return self.menu_sign.open_drink(
            drink
        )

    def tap_menu_back(
        self
    ):
        if not hasattr(
            self,
            "menu_sign"
        ):
            raise RuntimeError(
                "Bar counter has no menu sign."
            )

        UniverseLogger.event(
            "BAR COUNTER MENU BACK TAP"
        )

        return self.menu_sign.back()




