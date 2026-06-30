import random

class Universe:
    def __init__(self, name):
        self.name = name
class MeetingPlace:

    def __init__(self, universe):
        self.universe = universe
        self.entities = []
        self.events = []
        self.tick_count = 0

        print("🤝 MEETING PLACE INITIALIZED")

    def add_entity(self, entity):
        self.entities.append(entity)
        print(f"🤝 MP: entity joined {entity.name}")

    def emit_event(self, event):
        self.events.append(event)
        print(f"📡 MP EVENT: {event}")

    def tick(self):
        self.tick_count += 1

        print(f"\n🤝 MEETING PLACE TICK {self.tick_count}")

        # zatím jen “idle loop”
        self._clear_events()

    def _clear_events(self):
        self.events = []

    def process_interactions(self):

    # KROK A1: kontrola minimálního počtu entit
        if len(self.entities) < 2:
            return

        sorted_entities = sorted(self.entities, key=lambda e:e.energy, reverse=True)

        a = sorted_entities[0]
        b = sorted_entities[-1]

    # KROK A2: ochrana proti chybějícím atributům
        if not hasattr(a, "energy") or not hasattr(b, "energy"):
            return

        transfer = 0.5

        a.energy -= transfer
        b.energy += transfer

        self.emit_event(f"{a.name} -> {b.name} energy transfer {transfer}")

