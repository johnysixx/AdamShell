from .bartender import Bartender
from .terminals import BarTerminals
from .bar_counter import BarCounter
from .bouncer import Bouncer
from .dice_vial import DiceVial
from .fridge import BarFridge
from .reservoirs import BarEnergyReservoir, BarEntropyReservoir

class MeetingPlace:

    def __init__(self, universe):
        self.universe = universe
        self.entities = []
        self.events = []
        self.tick_count = 0
        self.bar_counter = BarCounter()
        self.dice_vial = DiceVial()
        self.fridge = BarFridge()
        self.energy_reservoir = BarEnergyReservoir()
        self.entropy_reservoir = BarEntropyReservoir()
        self.terminals = BarTerminals()
        self.bouncer = Bouncer()
        self.bartender = Bartender(
            self.bar_counter.hidden_story_book
        )

        self.access = {
            "from": [
                "eden",
                "library",
                "quantum_layer"
            ],
            "exit_to": [
                "library",
                "quantum_layer"
            ],
            "root_universe": False
        }

        self.permissions = {
            "god": "enter",
            "serpent": "enter",
            "pazuzu": "enter",
            "classical_probe_debug_entity": "enter"
        }

        self.state = {
            "type": "meeting_layer",
            "state": "initialized",
            "access": self.access,
            "permissions": self.permissions,
            "entities": self.entities,
            "bar_counter": self.bar_counter.name,
            "hidden_story_book": self.bar_counter.hidden_story_book.name,
            "bar_cloth": self.bar_counter.bar_cloth,
            "milk_bowl": self.bar_counter.milk_bowl,
            "dice_vial": self.dice_vial.public_state,
            "fridge": self.fridge.public_state,
            "energy_reservoir": self.energy_reservoir.public_state,
            "entropy_reservoir": self.entropy_reservoir.public_state,
            "terminals": self.terminals.terminals,
            "bouncer": self.bouncer.name,
            "bartender": self.bartender.name
        }

        self.universe.world["meeting_place"] = self.state

        print("MEETING PLACE INITIALIZED")

    def can_enter(self, entity_name):
        return self.permissions.get(entity_name) == "enter"

    def add_entity(self, entity):
        entity_name = self._get_entity_name(entity)

        if not self.bouncer.can_enter(entity):
            print(f"MEETING PLACE ENTRY DENIED BY BOUNCER: {entity_name}")
            return

        self.entities.append(entity)
        self.universe.world["meeting_place"]["entities"] = self.entities

        print(f"MEETING PLACE: entity joined {entity_name}")
        self.emit_event(f"{entity_name} arrived at the bar")
        self.bartender.guest_arrives(entity_name)

        if self._is_cat(entity):
            self.handle_cat_after_entry(entity)

    def emit_event(self, event):
        self.events.append(event)
        self.bartender.observe_event(event)
        self.show_bar_story_count()
        print(f"MEETING PLACE EVENT: {event}")

    def guest_asks_about_dice_vial(self, guest_name):
        self.emit_event(f"{guest_name} asked about the dice vial")
        self.bartender.answer_about_dice_vial(guest_name)

    def handle_cat_after_entry(self, cat):
        self.serve_cat_milk(cat)

    def serve_cat_milk(self, cat):
        cat_name = self._get_entity_name(cat)

        milk = self.fridge.get_item("milk")
        milk_bowl = self.bar_counter.milk_bowl

        if milk is None:
            self.emit_event(f"{cat_name} could not be served milk because milk was missing")
            return

        self.bartender.pour_drink(cat_name, milk, milk_bowl)
        self.emit_event(f"{cat_name} drinks milk at the bar")

    def sync_reservoirs_to_world(self):
        self.universe.world["meeting_place"]["energy_reservoir"] = (
            self.energy_reservoir.public_state
        )
        self.universe.world["meeting_place"]["entropy_reservoir"] = (
            self.entropy_reservoir.public_state
        )

    def add_bar_entropy(self, source, amount_units):
        event = self.entropy_reservoir.add_entropy(source, amount_units)
        self.sync_reservoirs_to_world()
        self.emit_event(f"bar entropy increased from {source}")
        return event

    def quantum_entropy_tick(self, rng=None):
        event = self.entropy_reservoir.quantum_tick(rng)
        self.sync_reservoirs_to_world()
        self.emit_event("quantum entropy tick was stored in the bar")
        return event

    def serve_entropy_to_serpent(self, serpent):
        serpent_name = self._get_entity_name(serpent)

        event = self.entropy_reservoir.serve_entropy_to_serpent(
            self.energy_reservoir,
            serpent
        )

        self.sync_reservoirs_to_world()

        if event is None:
            self.emit_event(f"{serpent_name} could not be served entropy")
            return None

        self.emit_event(f"{serpent_name} drinks entropy at the bar")
        return event

    def tick(self):
        self.tick_count += 1
        print(f"MEETING PLACE TICK {self.tick_count}")
        self.bartender.idle_work()
        self._clear_events()

    def show_library_book_count(self, library):
        return self.terminals.show_book_count(library)

    def show_book_search_terminal(self):
        return self.terminals.show_book_search_placeholder()

    def show_random_library_excerpt(self, library):
        return self.terminals.show_random_excerpt(library)

    def show_bar_story_count(self):
        return self.terminals.show_bar_story_count(
            self.bar_counter
        )


    def _clear_events(self):
        self.events = []

    def _get_entity_name(self, entity):
        if isinstance(entity, dict):
            return entity.get("name")

        return getattr(entity, "name", None)

    def _is_cat(self, entity):
        if isinstance(entity, dict):
            return entity.get("type", None) == "cat"

        return getattr(entity, "type", None) == "cat"

    def process_interactions(self):
        if len(self.entities) < 2:
            return

        energy_entities = [
            entity for entity in self.entities
            if hasattr(entity, "energy")
        ]

        if len(energy_entities) < 2:
            return

        sorted_entities = sorted(
            energy_entities,
            key=lambda entity: entity.energy,
            reverse=True
        )

        a = sorted_entities[0]
        b = sorted_entities[-1]

        transfer = 0.5

        a.energy -= transfer
        b.energy += transfer

        self.emit_event(f"{a.name} -> {b.name} energy transfer {transfer}")
