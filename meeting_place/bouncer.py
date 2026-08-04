from universe.logger import UniverseLogger

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
            "lilith",
            "pazuzu_masculine_principle"
        ]

        self.denied_guests = []

        self.cat_policy = {
            "cats_are_always_allowed": True,
            "pet_cats_on_entry": True
        }

        self.cat_meow_history = []

        UniverseLogger.boot("BOUNCER CREATED")
        UniverseLogger.boot("BOUNCER STANDS OUTSIDE THE BAR")

    def can_enter(self, entity):
        entity_name = self._get_entity_name(entity)

        if self._is_cat(entity):
            meow_event = self.receive_cat_meow(
                entity
            )

            self.pet_cat(entity_name)

            allow_event = {
                "name": "bouncer_allowed_cat",
                "cat": entity_name,
                "meow_recognized": meow_event[
                    "recognized"
                ],
                "allowed": True
            }

            self.cat_meow_history.append(
                allow_event
            )

            UniverseLogger.event(
                f"BOUNCER ALLOWS CAT: {entity_name}"
            )

            return True

        if entity_name in self.denied_guests:
            UniverseLogger.event(f"BOUNCER DENIES ENTRY: {entity_name}")
            return False

        if entity_name in self.allowed_guests:
            UniverseLogger.event(f"BOUNCER ALLOWS ENTRY: {entity_name}")
            return True

        UniverseLogger.event(f"BOUNCER DENIES ENTRY: {entity_name}")
        return False

    def receive_cat_meow(
        self,
        cat
    ):
        cat_name = self._get_entity_name(
            cat
        )

        knows_meow = self._cat_knows_meow(
            cat
        )

        meow_event = {
            "name": "cat_meowed_at_bouncer",
            "cat": cat_name,
            "sound": "MEOW",
            "recognized": knows_meow
        }

        self.cat_meow_history.append(
            meow_event
        )

        UniverseLogger.event(
            f"CAT MEOWS AT BOUNCER: {cat_name}"
        )

        recognition_event = {
            "name": (
                "bouncer_recognized_cat_meow"
                if knows_meow
                else "bouncer_heard_unrecognized_meow"
            ),
            "cat": cat_name,
            "recognized": knows_meow
        }

        self.cat_meow_history.append(
            recognition_event
        )

        if knows_meow:
            UniverseLogger.event(
                "BOUNCER RECOGNIZES MEOW: "
                f"{cat_name}"
            )
        else:
            UniverseLogger.event(
                "BOUNCER HEARS ORDINARY CAT SOUND: "
                f"{cat_name}"
            )

        return recognition_event

    def _cat_knows_meow(
        self,
        cat
    ):
        if not isinstance(
            cat,
            dict
        ):
            return False

        return bool(
            cat.get(
                "learning",
                {}
            ).get(
                "meow_knowledge",
                {}
            ).get(
                "learned",
                False
            )
            and cat.get(
                "learning",
                {}
            ).get(
                "meow_knowledge",
                {}
            ).get(
                "can_speak",
                False
            )
        )

    def pet_cat(self, cat_name):
        UniverseLogger.event(f"BOUNCER PETS CAT: {cat_name}")

    def _get_entity_name(self, entity):
        if isinstance(entity, dict):
            return entity.get("world_key") or entity.get("name")

        return getattr(entity, "name", None)

    def _is_cat(self, entity):
        if isinstance(entity, dict):
            return entity.get("type") == "cat"

        return getattr(entity, "type", None) == "cat"
