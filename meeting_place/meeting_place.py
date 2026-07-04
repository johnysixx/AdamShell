from .bartender import Bartender
from .terminals import BarTerminals

class MeetingPlace:

    def __init__(self, universe):
        self.universe = universe
        self.entities = []
        self.events = []
        self.tick_count = 0
        self.bartender = Bartender()
        self.terminals = BarTerminals()

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
            "bartender": self.bartender.name,
            "terminals": self.terminals.terminals
        }

        self.universe.world["meeting_place"] = self.state

        print("MEETING PLACE INITIALIZED")

    def can_enter(self, entity_name):
        return self.permissions.get(entity_name) == "enter"

    def add_entity(self, entity):
        entity_name = self._get_entity_name(entity)

        if not self.can_enter(entity_name):
            print(f"MEETING PLACE ENTRY DENIED: {entity_name}")
            return

        self.entities.append(entity)
        self.universe.world["meeting_place"]["entities"] = self.entities

        print(f"MEETING PLACE: entity joined {entity_name}")
        self.bartender.guest_arrives(entity_name)

    def emit_event(self, event):
        self.events.append(event)
        self.bartender.observe_event(event)
        print(f"MEETING PLACE EVENT: {event}")

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


    def _clear_events(self):
        self.events = []

    def _get_entity_name(self, entity):
        if isinstance(entity, dict):
            return entity.get("name")

        return getattr(entity, "name", None)

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
