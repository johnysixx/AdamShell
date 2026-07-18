from .universe_manual import UniverseManual


class BackRoom:

    def __init__(self, universe_registry):
        self.name = "back_room"
        self.type = "bar_internal_room"

        self.universe_manual = UniverseManual(
            universe_registry
        )

        self.access = {
            "bartender": "main_door",
            "cats": "cat_door"
        }

        self.world_door = {
            "locked": True,
            "current_world_id": None,
            "has_cat_door": True
        }

        self.world_window = {
            "visible_world_id": None
        }

        self.world_keypad = {
            "allowed_user": "bartender",
            "entered_world_id": None
        }

    def inspect_world(self, observer_name):
        if observer_name != "bartender":
            return None

        visible_world_id = self.world_door.get(
            "current_world_id"
        )

        self.world_window["visible_world_id"] = (
            visible_world_id
        )

        return visible_world_id
