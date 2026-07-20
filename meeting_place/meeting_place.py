from .bartender import Bartender
from .terminals import BarTerminals
from .bar_counter import BarCounter
from .bouncer import Bouncer
from .dice_vial import DiceVial
from .dice_box import DiceBox
from .fridge import BarFridge
from .reservoirs import BarEnergyReservoir, BarEntropyReservoir
from .service_rules import BarServiceRules
from .back_room import BackRoom
from .glass_shelf import GlassShelf
from .bar_entity_policy import BarEntityPolicy
from .bar_geometry_terminal import BarGeometryTerminal
from .back_room_black_box import BackRoomBlackBox

class MeetingPlace:

    def __init__(self, universe):
        self.universe = universe
        self.universe.meeting_place = self

        self.entities = []
        self.events = []
        self.tick_count = 0
        self.bar_counter = BarCounter()
        self.glass_shelf = GlassShelf()
        self.bar_entity_policy = BarEntityPolicy()

        self.dice_vial = DiceVial()
        self.dice_box = DiceBox()
        self.fridge = BarFridge()
        self.energy_reservoir = BarEnergyReservoir()
        self.entropy_reservoir = BarEntropyReservoir()
        self.terminals = BarTerminals()
        self.geometry_terminal = BarGeometryTerminal()
        self.bouncer = Bouncer()
        self.service_rules = BarServiceRules()
        self.back_room = BackRoom(
            self.universe.universe_registry
        )

        self.back_room_black_box = (
            BackRoomBlackBox()
        )

        self.total_entropy_served_today = 0
        self.total_entropy_served_ever = 0
        self.entropy_terminal = {
            "name": "entropy_terminal",
            "type": "bar_terminal",
            "total_entropy_served_today": self.total_entropy_served_today,
            "total_entropy_served_ever": self.total_entropy_served_ever
        }
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
            "dice_box": self.dice_box.public_state,
            "fridge": self.fridge.public_state,
            "energy_reservoir": self.energy_reservoir.public_state,
            "entropy_reservoir": self.entropy_reservoir.public_state,
            "terminals": self.terminals.terminals,
            "bouncer": self.bouncer.name,
            "service_rules": "bar_service_rules",
            "entropy_terminal": self.entropy_terminal,
            "bartender": self.bartender.name
        }

        self.universe.world["meeting_place"] = self.state

        print("MEETING PLACE INITIALIZED")

    def can_enter(self, entity_name):
        return self.permissions.get(entity_name) == "enter"

    def add_entity(self, entity):
        entity_name = self._get_entity_name(entity)

        if self._is_cat(entity):
            self.bar_counter.red_button.clear_alarm()

        if not self.bouncer.can_enter(entity):
            print(f"MEETING PLACE ENTRY DENIED BY BOUNCER: {entity_name}")
            return

        self.bartender.prepare_for_guest()

        self.entities.append(entity)
        entity["current_layer"] = "meeting_place"
        self.universe.world["meeting_place"]["entities"] = self.entities

        print(f"MEETING PLACE: entity joined {entity_name}")
        self.emit_event(f"{entity_name} arrived at the bar")
        self.bartender.guest_arrives(entity_name)

        if self._is_cat(entity):
            self.universe.statistics.record_cat_arrived()
            self.geometry_terminal.cat_arrived(entity_name)
            self.handle_cat_after_entry(entity)

    def emit_event(self, event):
        self.events.append(event)

        self.back_room_black_box.record(
            event=event,
            source="meeting_place",
            tick=self.tick_count
        )

        self.bartender.observe_event(event)
        self.show_bar_story_count()

        print(f"MEETING PLACE EVENT: {event}")

    def guest_asks_about_dice_vial(self, guest_name):
        self.emit_event(f"{guest_name} asked about the dice vial")
        self.bartender.answer_about_dice_vial(guest_name)

    def handle_cat_created(self, cat_id):
        self.geometry_terminal.cat_detected(cat_id)
        self.bar_counter.red_button.activate_alarm()

    def handle_cat_after_entry(self, cat):
        self.serve_cat_milk(cat)

    def serve_cat_milk(self, cat):
        cat_name = self._get_entity_name(cat)

        milk = self.fridge.get_item("milk")
        milk_bowl = self.bar_counter.milk_bowl

        if milk is None:
            self.emit_event(f"{cat_name} could not be served milk because milk was missing")
            return

        self.bartender.serve_without_order(
            cat_name,
            milk,
            milk_bowl
        )
        self.emit_event(f"{cat_name} drinks milk at the bar")

    def sync_entropy_terminal_to_world(self):
        self.entropy_terminal["total_entropy_served_today"] = (
            self.total_entropy_served_today
        )
        self.entropy_terminal["total_entropy_served_ever"] = (
            self.total_entropy_served_ever
        )

        self.universe.world["meeting_place"]["entropy_terminal"] = (
            self.entropy_terminal
        )

    def sync_reservoirs_to_world(self):
        self.universe.world["meeting_place"]["energy_reservoir"] = (
            self.energy_reservoir.public_state
        )
        self.universe.world["meeting_place"]["entropy_reservoir"] = (
            self.entropy_reservoir.public_state
        )

    def add_bar_energy(self, source, amount_j):
        event = self.energy_reservoir.add_energy(source, amount_j)
        self.sync_reservoirs_to_world()
        self.emit_event(f"bar energy increased from {source}")
        return event

    def add_bar_entropy(self, source, amount_units):
        event = self.entropy_reservoir.add_entropy(source, amount_units)
        self.sync_reservoirs_to_world()
        self.emit_event(f"bar entropy increased from {source}")
        return event

    def serve_energy(self, entity):
        from universe.pre_cosmic_rules import ENERGY_SERVING_J

        entity_name = self._get_entity_name(entity)
        entity_type = self._get_entity_type(entity)

        if entity_type not in ["god", "idea_entity"]:
            self.emit_event(f"{entity_name} could not be served energy")
            return None

        try:
            reservoir_event = self.energy_reservoir.spend_energy(
                f"energy_serving_for_{entity_name}",
                ENERGY_SERVING_J
            )
        except ValueError:
            self.sync_reservoirs_to_world()
            self.emit_event(f"{entity_name} could not be served energy because bar energy was missing")
            return None

        service_effect = self.service_rules.apply_energy_drink(entity)

        self.sync_reservoirs_to_world()
        self.emit_event(f"{entity_name} drinks energy at the bar")
        self.emit_event(f"{entity_name} energy drink effect applied")

        return {
            "reservoir_event": reservoir_event,
            "service_effect": service_effect
        }

    def quantum_entropy_tick(self, rng=None):
        event = self.entropy_reservoir.quantum_tick(rng)
        self.sync_reservoirs_to_world()
        self.emit_event("quantum entropy tick was stored in the bar")
        return event

    def serve_entropy(self, entity):
        entity_name = self._get_entity_name(entity)
        entity_type = self._get_entity_type(entity)

        if entity_type not in ["god", "idea_entity"]:
            self.emit_event(f"{entity_name} could not be served entropy")
            return None

        event = self.entropy_reservoir.serve_entropy(
            self.energy_reservoir,
            entity_name
        )

        self.sync_reservoirs_to_world()

        if event is None:
            self.emit_event(f"{entity_name} could not be served entropy")
            return None

        self.total_entropy_served_today += 1
        self.total_entropy_served_ever += 1
        self.sync_entropy_terminal_to_world()

        if self.total_entropy_served_ever % 10 == 0:
            secret_event = self.dice_vial.roll_secretly()

            if secret_event["quantum_tick_requested"]:
                self.quantum_entropy_tick()

            if secret_event["box_created"]:
                self.universe.create_quantum_box()



        effect = self.service_rules.apply_entropy_drink(
            entity,
            event.get("entity_energy_gain_j", 0.0)
        )

        self.emit_event(f"{entity_name} drinks entropy at the bar")
        self.emit_event(f"{entity_name} entropy drink effect applied")

        return {
            "reservoir_event": event,
            "service_effect": effect
        }

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

    def ask_bartender_about_dice_box(self, entity=None):
        return self.dice_box.answer_about_contents()

    def ask_bartender_about_d20(self, entity=None):
        return self.dice_box.answer_about_d20()

    def _get_entity_name(self, entity):
        if isinstance(entity, dict):
            return entity.get("name")

        return getattr(entity, "name", None)

    def _get_entity_type(self, entity):
        if isinstance(entity, dict):
            return entity.get("type")

        return getattr(entity, "type", None)

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
