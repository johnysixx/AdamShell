class IdeaEntities:

    def __init__(self, universe):
        self.universe = universe
        self.idea_entities = []
        self.events = []
        self.tick_count = 0

        self.permissions = {
            "can_exist_before_form": True,
            "can_influence": True,
            "can_become_process": True
        }

        self.universe.world["idea_entities"] = {
            "type": "entity_layer",
            "state": "created",
            "idea_entities": self.idea_entities,
            "permissions": self.permissions
        }

        print("IDEA ENTITIES LAYER CREATED")

    def create_idea_entity(self, name, role="primordial_idea_entity", active=False):
        idea_entity = {
            "name": name,
            "type": "idea_entity",
            "role": role,
            "state": "created",
            "active": active,
            "forbidden": False,
            "permissions": self.permissions
        }

        self.idea_entities.append(idea_entity)
        self.universe.world["idea_entities"]["idea_entities"] = self.idea_entities

        print(f"IDEA ENTITY CREATED: {name}")
        return idea_entity

    def emit_event(self, event):
        self.events.append(event)
        print(f"IDEA ENTITIES EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        print(f"IDEA ENTITIES TICK {self.tick_count}")
        self._clear_events()

    def _clear_events(self):
        self.events = []
        