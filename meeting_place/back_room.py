from .universe_manual import UniverseManual
from .cronenberg_pen_terminal import CronenbergPenTerminal
from .bar_objects import BackRoomAccess, WorldDoor, WorldWindow, WorldKeypad


class BackRoom:

    def __init__(self, universe_registry):
        self.name = "back_room"
        self.type = "bar_internal_room"

        self.bar_ingredients = {
            "rum": {
                "available": True,
                "fundamental": True,
                "serve_directly": True,
                "category": "basic_drink"
            },
            "whisky": {
                "available": True,
                "fundamental": True,
                "serve_directly": True,
                "category": "basic_drink"
            },
            "vodka": {
                "available": True,
                "fundamental": True,
                "serve_directly": True,
                "category": "basic_drink"
            },
            "gin": {
                "available": True,
                "fundamental": True,
                "serve_directly": True,
                "category": "basic_drink"
            },
            "beer": {
                "available": True,
                "fundamental": True,
                "serve_directly": True,
                "category": "basic_drink"
            },
            "wine": {
                "available": True,
                "fundamental": True,
                "serve_directly": True,
                "category": "basic_drink"
            },
            "mead": {
                "available": True,
                "fundamental": True,
                "serve_directly": True,
                "category": "basic_drink"
            },
            "apple_cider": {
                "available": True,
                "fundamental": True,
                "serve_directly": True,
                "category": "basic_drink"
            }
        }

        self.universe_manual = UniverseManual(
            universe_registry
        )

        self.cronenberg_pen_terminal = CronenbergPenTerminal()

        self.access = BackRoomAccess(
            bartender="main_door",
            cats="cat_door"
        )

        self.world_door = WorldDoor(
            locked=True,
            current_world_id=None,
            cat_door=None
        )

        self.world_window = WorldWindow(
            visible_world_id=None
        )

        self.world_keypad = WorldKeypad(
            allowed_user="bartender",
            entered_world_id=None
        )

    def attach_world_cat_door(
        self,
        cat_door
    ):
        self.world_door.cat_door = (
            cat_door
        )

        return cat_door

    def inspect_world(self, observer_name):
        if observer_name != "bartender":
            return None

        visible_world_id = self.world_door.current_world_id

        self.world_window.visible_world_id = (
            visible_world_id
        )

        return visible_world_id

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "access": self.access.to_dict(),
            "universe_manual": (
                self.universe_manual.public_state
            ),
            "world_door": {
                "locked": (
                    self.world_door.locked
                ),
                "current_world_id": (
                    self.world_door.current_world_id
                ),
                "cat_door": (
                    self.world_door.cat_door.public_state
                    if self.world_door.cat_door is not None
                    else None
                )
            },
            "world_window": self.world_window.to_dict(),
            "world_keypad": self.world_keypad.to_dict()
        }


