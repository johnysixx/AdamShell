from copy import deepcopy
from dataclasses import dataclass, field

from core.entity.component_object import ComponentObject


class BarObject(ComponentObject):
    pass


class BarOrigin(BarObject):
    pass


class BarShift(BarObject):
    pass


@dataclass(slots=True)
class BarConversationLine:
    speaker: str
    meaning: str

    def to_dict(self):
        return {
            "speaker": self.speaker,
            "meaning": self.meaning,
        }


@dataclass(slots=True)
class BarConversation:
    started: bool = False
    participants: list[str] = field(
        default_factory=list
    )
    content: list[BarConversationLine] = field(
        default_factory=list
    )

    def begin(
        self,
        participants
    ):
        self.started = True
        self.participants = list(
            participants
        )
        self.content = []
        return self

    def add_line(
        self,
        speaker,
        meaning
    ):
        line = BarConversationLine(
            speaker=speaker,
            meaning=meaning,
        )
        self.content.append(
            line
        )
        return line

    def to_dict(self):
        return {
            "started": self.started,
            "participants": list(
                self.participants
            ),
            "content": [
                line.to_dict()
                for line
                in self.content
            ],
        }


class BarServingVessel:

    def fill(
        self,
        contents
    ):
        self.state = "filled"
        self.contains = contents
        return self

    def empty(self):
        self.state = "empty"
        self.contains = None
        return self


class BarCloth(BarObject):
    pass


class MilkBowl(
    BarServingVessel,
    BarObject
):
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
class BarGlass(BarServingVessel):
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
    contains: str | None = None

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
        if self.contains is not None:
            result["contains"] = self.contains
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
class BarSecurityConfiscation:
    guest: str | None
    existence_pct: float
    energy_j: float
    existence_world: str | None = None
    removed_existence_pct: float | None = None

    def record_existence_removal(
        self,
        world,
        removed_existence_pct
    ):
        self.existence_world = world
        self.removed_existence_pct = float(
            removed_existence_pct
        )

    def to_dict(self):
        result = {
            "guest": self.guest,
            "existence_pct": self.existence_pct,
            "energy_j": self.energy_j,
        }

        if self.existence_world is not None:
            result[
                "existence_world"
            ] = self.existence_world

        if self.removed_existence_pct is not None:
            result[
                "removed_existence_pct"
            ] = self.removed_existence_pct

        return result


@dataclass(slots=True)
class BarSecurityEnergyAllocation:
    entity_energy_j: float
    multiverse_energy_j: float
    bar_energy_j: float

    @classmethod
    def from_confiscated_energy(
        cls,
        energy_j
    ):
        energy_j = float(
            energy_j
        )

        return cls(
            entity_energy_j=
                energy_j * 0.25,
            multiverse_energy_j=
                energy_j * 0.5,
            bar_energy_j=
                energy_j * 0.25,
        )

    def to_dict(self):
        return {
            "entity_energy_j": self.entity_energy_j,
            "multiverse_energy_j": self.multiverse_energy_j,
            "bar_energy_j": self.bar_energy_j,
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

@dataclass(slots=True)
class BarDrink:
    name: str
    type: str
    category: str | None = None
    ingredients: dict = field(default_factory=dict)
    price_basis: str | None = None
    effects: dict = field(default_factory=dict)
    base: str | None = None
    garnish: dict | None = None
    preparation: dict | None = None

    def to_dict(self):
        result = {
            "name": self.name,
            "type": self.type,
        }

        if self.category is not None:
            result["category"] = self.category

        if self.ingredients:
            result["ingredients"] = deepcopy(
                self.ingredients
            )

        if self.price_basis is not None:
            result["price_basis"] = self.price_basis

        if self.effects:
            result["effects"] = deepcopy(
                self.effects
            )

        if self.base is not None:
            result["base"] = self.base

        if self.garnish is not None:
            result["garnish"] = deepcopy(
                self.garnish
            )

        if self.preparation is not None:
            result["preparation"] = deepcopy(
                self.preparation
            )

        return result


@dataclass(slots=True)
class BarIngredientStock:
    name: str
    available: bool
    fundamental: bool
    serve_directly: bool = False
    category: str | None = None
    shots: float | int | None = None
    unit: str | None = None

    def consume(
        self,
        amount
    ):
        amount = float(
            amount
        )

        if self.shots is None:
            raise ValueError(
                f"Ingredient {self.name} "
                "has no consumable shot stock."
            )

        if (
            float(self.shots)
            < amount
        ):
            return False

        self.shots -= amount

        if (
            isinstance(
                self.shots,
                float
            )
            and self.shots.is_integer()
        ):
            self.shots = int(
                self.shots
            )

        return True

    def to_dict(self):
        result = {
            "name":
                self.name,
            "available":
                self.available,
            "fundamental":
                self.fundamental,
            "serve_directly":
                self.serve_directly,
        }

        if self.category is not None:
            result[
                "category"
            ] = self.category

        if self.shots is not None:
            result[
                "shots"
            ] = self.shots

        if self.unit is not None:
            result[
                "unit"
            ] = self.unit

        return result


@dataclass(slots=True)
class RecipeIngredientRequirement:
    shots: float | int = 1
    consumed: bool = False
    use: str | None = None
    unit: str | None = None

    def to_dict(self):
        result = {
            "shots":
                self.shots,
            "consumed":
                self.consumed,
        }

        if self.use is not None:
            result[
                "use"
            ] = self.use

        if self.unit is not None:
            result[
                "unit"
            ] = self.unit

        return result


@dataclass(slots=True)
class RecipeTasting:
    guest: str
    liked: bool
    comment: str | None = None

    def to_dict(self):
        return {
            "guest":
                self.guest,
            "liked":
                self.liked,
            "comment":
                self.comment,
        }


@dataclass(slots=True)
class DrinkRecipe:
    name: str
    origin: str

    ingredients: (
        dict[
            str,
            RecipeIngredientRequirement
        ]
        | list[str]
    )

    hidden: bool = False
    learned: bool = True
    teacher: str | None = None
    category: str | None = None

    effects: dict = field(
        default_factory=dict
    )

    price_basis: str | None = None
    status: str | None = None

    tastings: list[RecipeTasting] = field(
        default_factory=list
    )

    votes_for: int = 0
    votes_against: int = 0
    approved: bool = False
    menu_added_day: int | None = None
    revision: int | None = None
    revision_reason: str | None = None

    def reveal(
        self,
        teacher
    ):
        self.hidden = False
        self.learned = True
        self.teacher = teacher
        self.origin = (
            "taught_by_god"
        )

        return self

    def record_tasting(
        self,
        guest,
        liked,
        comment=None
    ):
        for existing in self.tastings:

            if (
                existing.guest
                == guest
            ):
                raise ValueError(
                    "Guest already tasted "
                    "this cocktail."
                )

        tasting = RecipeTasting(
            guest=guest,
            liked=bool(liked),
            comment=comment,
        )

        self.tastings.append(
            tasting
        )

        if tasting.liked:
            self.votes_for += 1
        else:
            self.votes_against += 1

        if len(self.tastings) == 5:

            if self.votes_for >= 4:
                self.approved = True
                self.status = (
                    "approved"
                )

            else:
                self.approved = False
                self.status = (
                    "rejected"
                )

        return tasting

    def to_dict(self):

        if isinstance(
            self.ingredients,
            dict
        ):
            ingredients = {
                name:
                    requirement.to_dict()
                for name, requirement
                in self.ingredients.items()
            }

        else:
            ingredients = list(
                self.ingredients
            )

        result = {
            "name":
                self.name,
            "origin":
                self.origin,
            "hidden":
                self.hidden,
            "learned":
                self.learned,
            "teacher":
                self.teacher,
            "ingredients":
                ingredients,
            "effects":
                dict(self.effects),
            "votes_for":
                self.votes_for,
            "votes_against":
                self.votes_against,
            "approved":
                self.approved,
        }

        if self.category is not None:
            result[
                "category"
            ] = self.category

        if self.price_basis is not None:
            result[
                "price_basis"
            ] = self.price_basis

        if self.status is not None:
            result[
                "status"
            ] = self.status

        if self.tastings:
            result[
                "tastings"
            ] = [
                item.to_dict()
                for item
                in self.tastings
            ]

        elif self.status is not None:
            result[
                "tastings"
            ] = []

        if self.menu_added_day is not None:
            result[
                "menu_added_day"
            ] = self.menu_added_day

        if self.revision is not None:
            result[
                "revision"
            ] = self.revision

        if self.revision_reason is not None:
            result[
                "revision_reason"
            ] = self.revision_reason

        return result
