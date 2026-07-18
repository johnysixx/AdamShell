class RootUniverse:

    def __init__(self, universe):
        self.universe = universe
        self.events = []
        self.tick_count = 0

        registry = getattr(
            self.universe,
            "universe_registry",
            None
        )

        if registry is None:
            raise RuntimeError(
                "Root Universe requires UniverseRegistry"
            )

        self.universe_id = registry.register_universe(
            name="root_universe",
            universe_type="independent_root_reality"
        )

        self.state = {
            "name": "root_universe",
            "type": "independent_root_reality",
            "state": "created",
            "creator": "god",
            "administrator": "god",
            "part_of_physics": True,

            "access": {
                "god": "write",
                "serpent": "read",
                "adam": "read",
                "eve": "read",
                "pazuzu": "read",
                "classical_probe_debug_entity": "read"
            },

            "permissions": {
                "can_modify": ["god"],
                "can_read": [
                    "god",
                    "serpent",
                    "adam",
                    "eve",
                    "pazuzu",
                    "classical_probe_debug_entity"
                ]
            },

            "eden": {
                "role": "sandbox",
                "history_origin": True,
                "direct_parent": False
            },

            "eden_influence": [],
            "history_started": False,
            "awaiting_adam_and_eve": True,
            "history": []
        }

        self.universe.physics["root_universe"] = self.state
        self.universe.world["root_universe"] = self.state

        print("ROOT UNIVERSE INITIALIZED")

    def can_read(self, entity_name):
        return entity_name in self.state["permissions"]["can_read"]

    def can_modify(self, entity_name):
        return entity_name in self.state["permissions"]["can_modify"]

    def apply_eden_influence(self, entity_name, influence):
        if not self.can_modify(entity_name):
            print(f"ROOT UNIVERSE MODIFY DENIED: {entity_name}")
            return

        self.state["eden_influence"].append(influence)
        print(f"ROOT UNIVERSE EDEN INFLUENCE: {influence}")

    def start_history(self, entity_name):
        if not self.can_modify(entity_name):
            print(f"ROOT UNIVERSE HISTORY START DENIED: {entity_name}")
            return

        self.state["history_started"] = True
        self.state["awaiting_adam_and_eve"] = False
        print("ROOT UNIVERSE HISTORY STARTED")

    def emit_event(self, event):
        self.events.append(event)
        print(f"ROOT UNIVERSE EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        print(f"ROOT UNIVERSE TICK {self.tick_count}")
        self._clear_events()

    def _clear_events(self):
        self.events = []