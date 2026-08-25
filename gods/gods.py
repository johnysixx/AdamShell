from universe.pre_cosmic_rules import GOD_INITIAL_ENERGY_J
from universe.logger import UniverseLogger

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

        UniverseLogger.boot("GODS LAYER CREATED")

    def create_god(self, name, role="creator_entity"):
        god = {
            "name": name,
            "type": "god",
            "role": role,
            "state": "present",
            "active": True,
            "forbidden": False,

            "existence_pct": 100.0,

            "native_world": "gods_layer",

            "existence_by_world": {
                "gods_layer": 100.0,
                "idea_universe": 100.0,
                "root_universe": 0.0,
                "eden": 0.0
            },

            "departure_intent": {
                "wants_to_leave": False
            },

            "creative_will": 0.0,
            "energy_j": GOD_INITIAL_ENERGY_J,
            "creation_capacity": 0.0,

            "divine_attributes": {
                "aseity": True,
                "eternity": True,
                "transcendence": True,
                "immanence": True,
                "creative_authority": True,
                "sovereignty": "potential",
                "providence": "potential",
                "omniscience": "potential",
                "omnipotence": "potential",
                "omnipresence": "potential",
                "immutability": "limited_by_story_state",
                "simplicity": "symbolic",
                "perfect_goodness": "not_assumed"
            },

            "creation_limits": {
                "limited_by_existence_pct": True,
                "limited_by_creative_will": True,
                "limited_by_current_reality_rules": True
            },

            "permissions": self.permissions,
            "created_entities": [],
            "administers": [],

            "book": {
                "type": "god_book",
                "author": name,
                "state": "being_written",
                "energy_j": 0.0,
                "location": "with_author",
                "entries": [
                    {
                        "event": "god_born",
                        "subject": name
                    }
                ]
            }
        }

        self.gods.append(god)
        self.universe.world["gods"]["gods"] = self.gods

        UniverseLogger.event(f"GOD CREATED: {name}")
        return god

    def emit_event(self, event):
        self.events.append(event)
        UniverseLogger.event(f"GODS EVENT: {event}")

    def tick(self):
        self.tick_count += 1
        UniverseLogger.event(f"GODS TICK {self.tick_count}")
        self._clear_events()

    def _clear_events(self):
        self.events = []




    def assume_mask(
        self,
        god,
        mask_name,
        role
    ):
        knowledge = god.setdefault(
            "knowledge",
            set()
        )

        research_book = god.setdefault(
            "research_book",
            []
        )

        masks = god.setdefault(
            "masks",
            {}
        )

        mask = {
            "name": mask_name,
            "type": "god_mask",
            "role": role,
            "active": True,
            "mask_of": god,
            "knowledge": knowledge,
            "research_book": research_book
        }

        masks[
            mask_name
        ] = mask

        god[
            "active_mask"
        ] = mask_name

        return mask

    def release_mask(
        self,
        god,
        mask_name
    ):
        masks = god.get(
            "masks",
            {}
        )

        if mask_name not in masks:
            raise RuntimeError(
                f"Mask not found: {mask_name}"
            )

        mask = masks[
            mask_name
        ]

        mask["active"] = False

        if god.get("active_mask") == mask_name:
            god["active_mask"] = None

        return {
            "released_mask": mask_name,
            "god": god,
            "mask": mask
        }



