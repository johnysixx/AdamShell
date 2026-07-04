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

        self.hidden_story_book = BarStoryBook()

        print("BAR COUNTER CREATED")
        print("BAR STORY BOOK HIDDEN UNDER BAR COUNTER")

    def write_bar_story(self, event):
        self.hidden_story_book.write_entry(event)

    def read_bar_stories(self):
        return self.hidden_story_book.read_entries()