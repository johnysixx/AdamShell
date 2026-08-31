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

from dataclasses import dataclass, field


@dataclass(slots=True)
class BarHexCell:
    name: str
    x: float
    y: float
    kind: str
    walkable: bool = True
    standing: bool = False
    seating: bool = False
    door: bool = False
    connects_to: str | None = None
    immutable: bool = False
    furniture_allowed: bool = True
    ring: int | None = None
    occupied_by: str | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "kind": self.kind,
            "walkable": self.walkable,
            "standing": self.standing,
            "seating": self.seating,
            "door": self.door,
            "connects_to": self.connects_to,
            "immutable": self.immutable,
            "furniture_allowed": self.furniture_allowed,
            "ring": self.ring,
            "occupied_by": self.occupied_by,
        }


@dataclass(slots=True)
class BarGlass:
    name: str | None
    type: str
    owner: str | None
    state: str
    dirt: float
    location: str
    kind: str | None = None
    reserved_for: str | None = None
    reservation_number: int | None = None
    created_for_entity: str | None = None
    capacity_litres: float | None = None

    def to_dict(self):
        result = {
            "name": self.name,
            "type": self.type,
            "owner": self.owner,
            "state": self.state,
            "dirt": self.dirt,
            "location": self.location,
        }
        if self.kind is not None:
            result["kind"] = self.kind
        if self.reserved_for is not None:
            result["reserved_for"] = self.reserved_for
        if self.reservation_number is not None:
            result["reservation_number"] = self.reservation_number
        if self.created_for_entity is not None:
            result["created_for_entity"] = self.created_for_entity
        if self.capacity_litres is not None:
            result["capacity_litres"] = self.capacity_litres
        return result


@dataclass(slots=True)
class BarInventoryItem:
    name: str
    type: str
    form: str
    state: str
    stored_in: str
    suitable_for: list[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "form": self.form,
            "state": self.state,
            "stored_in": self.stored_in,
            "suitable_for": list(self.suitable_for),
        }


@dataclass(slots=True)
class DarkEnergyBottle:
    name: str
    type: str
    location: str
    dark_energy_j: float

    def add_energy(self, amount_j):
        self.dark_energy_j += float(amount_j)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "dark_energy_j": self.dark_energy_j,
        }


@dataclass(slots=True)
class BarTabItem:
    drink: str
    drink_category: str | None = None

    def to_dict(self):
        return {
            "drink": self.drink,
            "drink_category": self.drink_category,
        }


@dataclass(slots=True)
class BarTab:
    guest: str
    guest_type: str | None
    status: str = "open"
    paid: bool = False
    items: list[BarTabItem] = field(default_factory=list)
    latest_receipt_number: int | None = None

    def add_item(self, drink, drink_category=None):
        item = BarTabItem(
            drink=drink,
            drink_category=drink_category,
        )
        self.items.append(item)
        return item

    def to_dict(self):
        result = {
            "guest": self.guest,
            "guest_type": self.guest_type,
            "status": self.status,
            "paid": self.paid,
            "items": [item.to_dict() for item in self.items],
        }
        if self.latest_receipt_number is not None:
            result["latest_receipt_number"] = self.latest_receipt_number
        return result

