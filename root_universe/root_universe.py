from root_universe.root_universe_state import RootUniverseState
from universe.logger import UniverseLogger


class RootUniverse:

    def __init__(self, universe):
        self.universe = universe
        self.name = "root_universe"
        self.type = "independent_root_reality"

        registry = getattr(
            self.universe,
            "universe_registry",
            None,
        )

        if registry is None:
            raise RuntimeError(
                "Root Universe requires UniverseRegistry"
            )

        self.universe_id = registry.register_universe(
            name=self.name,
            universe_type=self.type,
        )

        self.root_universe_state = RootUniverseState()
        self.state = self.root_universe_state

        self.write_to_universe()

        UniverseLogger.boot("ROOT UNIVERSE INITIALIZED")

    @property
    def events(self):
        return self.root_universe_state.events

    @events.setter
    def events(self, value):
        self.root_universe_state.events = value

    @property
    def tick_count(self):
        return self.root_universe_state.tick_count

    @tick_count.setter
    def tick_count(self, value):
        self.root_universe_state.tick_count = value

    @property
    def public_state(self):
        state = self.root_universe_state.to_dict()

        return {
            "name": self.name,
            "type": self.type,
            "state": state["status"],
            "creator": state["creator"],
            "administrator": state["administrator"],
            "part_of_physics": state["part_of_physics"],
            "access": state["access"],
            "permissions": state["permissions"],
            "eden": state["eden"],
            "eden_influence": state["eden_influence"],
            "history_started": state["history_started"],
            "awaiting_adam_and_eve": (
                state["awaiting_adam_and_eve"]
            ),
            "history": state["history"],
            "root_universe_state": state,
        }

    def write_to_universe(self):
        public_state = self.public_state

        self.universe.physics["root_universe"] = public_state
        self.universe.world["root_universe"] = public_state
        self.universe.world["root_universe_state"] = (
            self.root_universe_state
        )

    def can_read(self, entity_name):
        return (
            entity_name
            in self.root_universe_state.permissions["can_read"]
        )

    def can_modify(self, entity_name):
        return (
            entity_name
            in self.root_universe_state.permissions["can_modify"]
        )

    def apply_eden_influence(self, entity_name, influence):
        if not self.can_modify(entity_name):
            UniverseLogger.event(
                "ROOT UNIVERSE MODIFY DENIED: "
                f"{entity_name}"
            )
            return

        self.root_universe_state.eden_influence.append(
            influence
        )
        self.write_to_universe()

        UniverseLogger.event(
            "ROOT UNIVERSE EDEN INFLUENCE: "
            f"{influence}"
        )

    def start_history(self, entity_name):
        if not self.can_modify(entity_name):
            UniverseLogger.event(
                "ROOT UNIVERSE HISTORY START DENIED: "
                f"{entity_name}"
            )
            return

        self.root_universe_state.history_started = True
        self.root_universe_state.awaiting_adam_and_eve = False
        self.write_to_universe()

        UniverseLogger.event(
            "ROOT UNIVERSE HISTORY STARTED"
        )

    def emit_event(self, event):
        self.events.append(event)
        self.write_to_universe()

        UniverseLogger.event(
            f"ROOT UNIVERSE EVENT: {event}"
        )

    def tick(self):
        self.tick_count += 1

        UniverseLogger.event(
            f"ROOT UNIVERSE TICK {self.tick_count}"
        )

        self._clear_events()
        self.write_to_universe()

    def _clear_events(self):
        self.events = []
