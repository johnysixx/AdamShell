class IdeaUniverse:

    def __init__(self, universe):
        self.universe = universe
        self.entities = []
        self.events = []
        self.tick_count = 0

        registry = getattr(
            self.universe,
            "universe_registry",
            None
        )

        if registry is None:
            raise RuntimeError(
                "Idea Universe requires UniverseRegistry"
            )

        self.universe_id = registry.register_universe(
            name="idea_universe",
            universe_type="pre_physical_idea_reality"
        )

        self.state = {
            "name": "idea_universe",
            "type": "pre_physical_idea_reality",
            "state": "created",
            "part_of_physics": False,
            "entities": self.entities,
            "events": self.events
        }

        self.universe.world["idea_universe"] = self.state

        print("IDEA UNIVERSE INITIALIZED")

    def add_entity(self, entity):
        entity["origin_layer"] = "idea_universe"
        entity["current_layer"] = "idea_universe"

        self.entities.append(entity)

        print(
            f"IDEA UNIVERSE ENTITY BORN: "
            f"{entity.get('name')}"
        )
