class BarStoryBook:

    def __init__(self):
        self.name = "bar_story_book"
        self.type = "hidden_story_book"
        self.location = "under_bar_counter"
        self.entries = []

        print("BAR STORY BOOK CREATED")

    def write_entry(self, event):
        self.entries.append(event)
        print(f"BAR STORY BOOK ENTRY: {event}")

    def read_entries(self):
        return self.entries


class BarCounter:

    def __init__(self):
        self.name = "bar_counter"
        self.type = "bar_furniture"
        self.state = "created"

        print("BAR COUNTER CREATED")

        self.hidden_story_book = BarStoryBook()

        self.bar_cloth = {
            "name": "bar_cloth",
            "type": "bar_tool",
            "location": "under_bar_counter",
            "visible_use": "wiping_bar"
        }

        print("BAR CLOTH PLACED UNDER BAR COUNTER")

        self.milk_bowl = {
            "name": "milk_bowl",
            "type": "bar_serving_object",
            "state": "empty",
            "location": "under_bar_counter_next_to_bar_cloth",
            "intended_use": "serving_milk_to_cats"
        }

        print("MILK BOWL PLACED UNDER BAR COUNTER NEXT TO BAR CLOTH")

    def write_bar_story(self, event):
        self.hidden_story_book.write_entry(event)

    def read_bar_stories(self):
        return self.hidden_story_book.read_entries()