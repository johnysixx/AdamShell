from universe.logger import UniverseLogger

class Bartender:

    def __init__(self, story_book, name="bartender"):
        self.name = name
        self.type = "bar_observer"
        self.state = "present"
        self.story_book = story_book
        self.current_location = "meeting_place"

        self.origin = {
            "layer": "meeting_place",
            "event": "bartender was born in the bar"
        }


        self.event_memory = []

        self.regular_drinks = {}
        self.known_histories = {}
        self.known_guests = set()
        self.cat_meow_history = []

        self.current_task = "wiping_glasses"
        self.glasses_clean = False
        self.bar_counter_clean = False

        UniverseLogger.boot("BARTENDER CREATED")

    def answer_about_lemonade_origin(self):
        answer = (
            "When life gives you lemons, "
            "make lemonade."
        )

        UniverseLogger.event(
            f"BARTENDER ANSWERS ABOUT LEMONADE: {answer}"
        )

        return answer

    def respond_to_red_button_alarm(
        self,
        red_button,
        available=True
    ):
        if not red_button.alarm_active:
            UniverseLogger.event("BARTENDER HEARS NO RED BUTTON ALARM")
            return False

        if not available:
            UniverseLogger.event("BARTENDER DOES NOT RESPOND TO RED BUTTON ALARM")
            return False

        UniverseLogger.event("BARTENDER RESPONDS TO RED BUTTON ALARM")
        return red_button.press()

    def observe_event(self, event):
        self.event_memory.append(
            event
        )

        UniverseLogger.event(
            f"BARTENDER OBSERVED EVENT: {event}"
        )

    def end_shift(
        self
    ):
        shift_entries = []

        for event in self.event_memory:
            if not isinstance(
                event,
                dict
            ):
                continue

            if (
                event.get("name")
                != "bar_security_incident"
            ):
                continue

            resolution = event.get(
                "resolution"
            )

            if (
                resolution
                != "ejected_and_blacklisted"
            ):
                continue

            entry = {
                "type": "bartender_shift_story",
                "subject": event.get(
                    "offender"
                ),
                "observed_reason": event.get(
                    "reason"
                ),
                "observed_outcome": "ejected"
            }

            self.story_book.write_entry(
                entry
            )

            shift_entries.append(
                entry
            )

        self.event_memory = []


        UniverseLogger.event(
            "BARTENDER SHIFT ENDED"
        )

        return shift_entries

    def knows_guest(self, guest_name):
        return guest_name in self.known_guests

    def remember_guest(self, guest_name):
        self.known_guests.add(guest_name)

    def guest_arrives(self, guest_name):
        if self.knows_drink(guest_name):
            drink = self.regular_drinks[guest_name]
            UniverseLogger.event(f"BARTENDER ASKS: {guest_name}, do you want your usual {drink}?")
            return

        UniverseLogger.event(f"BARTENDER ASKS: {guest_name}, what would you like to drink?")

    def answer_about_dice_vial(self, guest_name):
        UniverseLogger.event(
            "BARTENDER ANSWERS: "
            "It is just a kind of dice. It was here before me."
        )

    def remember_first_order(self, guest_name, drink_name):
        if guest_name not in self.regular_drinks:
            self.regular_drinks[guest_name] = drink_name
            UniverseLogger.event(f"BARTENDER REMEMBERED FIRST ORDER: {guest_name} drinks {drink_name}")
            return

        UniverseLogger.event(f"BARTENDER ALREADY KNOWS: {guest_name} drinks {self.regular_drinks[guest_name]}")

    def knows_drink(self, guest_name):
        return guest_name in self.regular_drinks

    def mix_drink(self, guest_name, drink_name):
        self.remember_first_order(guest_name, drink_name)

        event = f"{guest_name} ordered {drink_name}"
        self.observe_event(event)

        UniverseLogger.event(f"BARTENDER MIXES DRINK: {drink_name} for {guest_name}")

    def pour_drink(self, guest_name, drink, serving_object):
        drink_name = self.get_drink_name(drink)
        serving_object_name = self.get_drink_name(serving_object)

        self.remember_first_order(guest_name, drink_name)

        if isinstance(serving_object, dict):
            serving_object["state"] = "filled"
            serving_object["contains"] = drink_name

        event = f"{guest_name} was served {drink_name} in {serving_object_name}"
        self.observe_event(event)

        UniverseLogger.event(
            f"BARTENDER POURS DRINK: "
            f"{drink_name} into {serving_object_name} for {guest_name}"
        )

        return serving_object

    def get_drink_name(self, drink):
        if isinstance(drink, dict):
            return drink.get("name")

        return getattr(drink, "name", drink)

    def idle_work(self):
        if not self.glasses_clean:
            self.current_task = "wiping_glasses"
            self.glasses_clean = True
            UniverseLogger.event("BARTENDER WIPES ALL GLASSES")
            return

        if not self.bar_counter_clean:
            self.current_task = "wiping_bar_counter"
            self.bar_counter_clean = True
            UniverseLogger.event("BARTENDER WIPES BAR COUNTER")
            return

        self.current_task = "observing_bar"
        UniverseLogger.event("BARTENDER OBSERVES THE BAR")

    def read_universe_manual(self, universe_manual):
        return universe_manual.read(self)

    def enter_back_room(self, back_room):
        access_route = back_room.access.get(
            self.name
        )

        if access_route != "main_door":
            return False

        self.current_location = back_room.name

        UniverseLogger.event("BARTENDER ENTERS BACK ROOM")

        return True

    def sleep_in_back_room(
            self,
            back_room,
            bar_has_guests
    ):
        if bar_has_guests:
            return False

        if self.current_location != back_room.name:
            entered = self.enter_back_room(
                back_room
            )

            if not entered:
                return False

        self.current_task = "sleeping"

        UniverseLogger.event("BARTENDER SLEEPS IN BACK ROOM")

        return True

    def prepare_for_guest(self):
        self.current_location = "meeting_place"
        self.current_task = "wiping_glasses"
        self.glasses_clean = False

        UniverseLogger.event("BARTENDER APPEARS BEHIND THE BAR")
        UniverseLogger.event("BARTENDER POLISHES A GLASS")

    def exchange_meow_with_cat(
        self,
        cat
    ):
        if isinstance(
            cat,
            dict
        ):
            cat_name = (
                cat.get("world_key")
                or cat.get("name")
            )

            meow = cat.get(
                "learning",
                {}
            ).get(
                "meow_knowledge",
                {}
            )

            cat_knows_meow = bool(
                meow.get(
                    "learned",
                    False
                )
                and meow.get(
                    "can_speak",
                    False
                )
            )

        else:
            cat_name = getattr(
                cat,
                "name",
                None
            )

            cat_knows_meow = False

        cat_event = {
            "name": "cat_meowed_at_bartender",
            "cat": cat_name,
            "sound": "MEOW",
            "understood": cat_knows_meow
        }

        self.cat_meow_history.append(
            cat_event
        )

        UniverseLogger.event(
            f"CAT MEOWS AT BARTENDER: {cat_name}"
        )

        reply_event = {
            "name": "bartender_replied_meow",
            "bartender": self.name,
            "cat": cat_name,
            "sound": "MEOW",
            "reply": True
        }

        self.cat_meow_history.append(
            reply_event
        )

        UniverseLogger.event(
            f"BARTENDER REPLIES MEOW TO: {cat_name}"
        )

        return {
            "cat_meow": cat_event,
            "bartender_meow": reply_event
        }

    def serve_without_order(
            self,
            guest_name,
            drink,
            serving_object
    ):
        drink_name = self.get_drink_name(drink)
        serving_object_name = self.get_drink_name(
            serving_object
        )

        if isinstance(serving_object, dict):
            serving_object["state"] = "filled"
            serving_object["contains"] = drink_name

        event = (
            f"{guest_name} was served "
            f"{drink_name} in {serving_object_name}"
        )

        self.observe_event(event)

        UniverseLogger.event(
            f"BARTENDER SERVES WITHOUT ORDER: "
            f"{drink_name} into {serving_object_name} "
            f"for {guest_name}"
        )

        return serving_object
