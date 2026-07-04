class Bartender:

    def __init__(self, story_book, name="bartender"):
        self.name = name
        self.type = "bar_observer"
        self.state = "present"
        self.story_book = story_book

        self.origin = {
            "layer": "meeting_place",
            "event": "bartender was born in the bar"
        }


        self.event_memory = []
        self.regular_drinks = {}
        self.known_histories = {}

        self.current_task = "wiping_glasses"
        self.glasses_clean = False
        self.bar_counter_clean = False

        print("BARTENDER CREATED")

    def observe_event(self, event):
        self.event_memory.append(event)
        self.story_book.write_entry(event)
        print(f"BARTENDER OBSERVED EVENT: {event}")

    def guest_arrives(self, guest_name):
        event = f"{guest_name} arrived at the bar"
        self.observe_event(event)

        if self.knows_drink(guest_name):
            drink = self.regular_drinks[guest_name]
            print(f"BARTENDER ASKS: {guest_name}, do you want your usual {drink}?")
            return

        print(f"BARTENDER ASKS: {guest_name}, what would you like to drink?")

    def remember_first_order(self, guest_name, drink_name):
        if guest_name not in self.regular_drinks:
            self.regular_drinks[guest_name] = drink_name
            print(f"BARTENDER REMEMBERED FIRST ORDER: {guest_name} drinks {drink_name}")
            return

        print(f"BARTENDER ALREADY KNOWS: {guest_name} drinks {self.regular_drinks[guest_name]}")

    def knows_drink(self, guest_name):
        return guest_name in self.regular_drinks

    def mix_drink(self, guest_name, drink_name):
        self.remember_first_order(guest_name, drink_name)

        event = f"{guest_name} ordered {drink_name}"
        self.observe_event(event)

        print(f"BARTENDER MIXES DRINK: {drink_name} for {guest_name}")

    def idle_work(self):
        if not self.glasses_clean:
            self.current_task = "wiping_glasses"
            self.glasses_clean = True
            print("BARTENDER WIPES ALL GLASSES")
            return

        if not self.bar_counter_clean:
            self.current_task = "wiping_bar_counter"
            self.bar_counter_clean = True
            print("BARTENDER WIPES BAR COUNTER")
            return

        self.current_task = "observing_bar"
        print("BARTENDER OBSERVES THE BAR")