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