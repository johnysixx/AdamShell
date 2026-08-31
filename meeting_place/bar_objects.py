from core.entity.component_object import ComponentObject


class BarObject(ComponentObject):
    pass


class BarOrigin(BarObject):
    pass


class BarShift(BarObject):
    pass


class BarCloth(BarObject):
    pass


class MilkBowl(BarObject):
    pass


class LemonTree(BarObject):
    pass


class BackRoomAccess(BarObject):
    pass


class WorldDoor(BarObject):
    pass


class WorldWindow(BarObject):
    pass


class WorldKeypad(BarObject):
    pass


class BouncerPrincipleAttributes(BarObject):
    pass


class CatEntryPolicy(BarObject):
    pass


class DiceVialContainer(BarObject):
    pass


class DiceVialMedium(BarObject):
    pass


class DiceVialDie(BarObject):
    pass


class LemonadeSign(BarObject):
    pass


class GeometryStatusSign(BarObject):
    pass


class CronenbergArea(BarObject):
    pass


class AmbientAroma(BarObject):
    pass


class EntropyTerminal(BarObject):
    pass


class MeetingPlaceAccess(BarObject):
    def to_dict(self):
        return {
            "from": list(self.from_layers),
            "exit_to": list(self.exit_to),
            "root_universe": self.root_universe,
        }


class MeetingPlacePermissions(BarObject):
    def allows(self, entity_name):
        return getattr(self, entity_name, None) == "enter"


class MeetingPlaceState(BarObject):
    pass


class CatD20Box(BarObject):
    pass
