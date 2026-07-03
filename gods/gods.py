class Gods:

    def __init__(self, universe):
        self.universe = universe
        self.gods = []
        self.events = []
        self.tick_count = 0

        self.permissions = {
            "can_create": True,
            "can_administer": True,
            "can_modify": True
        }

        self.universe.world["gods"] = {
            "type": "entity_layer",
            "state": "created",
            "gods": self.gods,
            "permissions": self.permissions
        }

        print("GODS LAYER CREATED")

    def create_god(self, name, role="creator_entity"):
        god = {
            "name": name,
            "type": "god",
            "role": role,
            "state": "present",
            "active": True,
            "forbidden": False,
            "permissions": self.permissions,
            "created_entities": [],
            "administers": []
        }

        self.gods.append(god)
        self.universe.world["gods"]["gods"] = self.gods

        print(f"GOD CREATED: {name}")
        return god

    def emit_event(self, event):
        self.events.append(event)
        print(f"GODS EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        print(f"GODS TICK {self.tick_count}")
        self._clear_events()

    def _clear_events(self):
        self.events = []