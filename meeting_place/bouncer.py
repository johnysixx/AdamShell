class Bouncer:

    def __init__(self):
        self.name = "bouncer"
        self.type = "bar_guard"
        self.state = "standing_outside_bar"

        self.origin = {
            "layer": "meeting_place",
            "event": "bouncer appeared at the bar entrance"
        }

        self.principle_attributes = {
            "principle": "masculine_principle",
            "domain": [
                "boundary",
                "protection",
                "threshold",
                "entry_control"
            ]
        }

        self.position = "outside_bar"
        self.knows_inside_events = False

        self.allowed_guests = [
            "god",
            "serpent",
            "pazuzu",
            "classical_probe_debug_entity",
            "lilith"
        ]

        self.denied_guests = [
            "pazuzu_masculine_principle"
        ]

        self.cat_policy = {
            "cats_are_always_allowed": True,
            "pet_cats_on_entry": True
        }

        print("BOUNCER CREATED")
        print("BOUNCER STANDS OUTSIDE THE BAR")

    def can_enter(self, entity):
        entity_name = self._get_entity_name(entity)

        if self._is_cat(entity):
            self.pet_cat(entity_name)
            print(f"BOUNCER ALLOWS CAT: {entity_name}")
            return True

        if entity_name in self.denied_guests:
            print(f"BOUNCER DENIES ENTRY: {entity_name}")
            return False

        if entity_name in self.allowed_guests:
            print(f"BOUNCER ALLOWS ENTRY: {entity_name}")
            return True

        print(f"BOUNCER DENIES ENTRY: {entity_name}")
        return False

    def pet_cat(self, cat_name):
        print(f"BOUNCER PETS CAT: {cat_name}")

    def _get_entity_name(self, entity):
        if isinstance(entity, dict):
            return entity.get("world_key") or entity.get("name")

        return getattr(entity, "name", None)

    def _is_cat(self, entity):
        if isinstance(entity, dict):
            return entity.get("type") == "cat"

        return getattr(entity, "type", None) == "cat"
    