import unittest

from core.entity.component_object import ComponentObject
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from meeting_place.bar_objects import (
    AmbientAroma,
    BackRoomAccess,
    BarCloth,
    BarOrigin,
    BarShift,
    BouncerPrincipleAttributes,
    CatD20Box,
    CatEntryPolicy,
    CronenbergArea,
    DiceVialContainer,
    DiceVialDie,
    DiceVialMedium,
    EntropyTerminal,
    GeometryStatusSign,
    LemonadeSign,
    LemonTree,
    MeetingPlaceAccess,
    MeetingPlacePermissions,
    MeetingPlaceState,
    MilkBowl,
    WorldDoor,
    WorldKeypad,
    WorldWindow,
)


class BarObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.universe.universe_registry = UniverseRegistry()
        self.bar = MeetingPlace(self.universe)

    def test_meeting_place_core_state_is_object_only(self):
        self.assertIsInstance(self.bar.cronenberg_area, CronenbergArea)
        self.assertIsInstance(self.bar.ambient_aroma, AmbientAroma)
        self.assertIsInstance(self.bar.entropy_terminal, EntropyTerminal)
        self.assertIsInstance(self.bar.access, MeetingPlaceAccess)
        self.assertIsInstance(self.bar.permissions, MeetingPlacePermissions)
        self.assertIsInstance(self.bar.state, MeetingPlaceState)

    def test_bar_counter_physical_objects_are_objects(self):
        self.assertIsInstance(self.bar.bar_counter.bar_cloth, BarCloth)
        self.assertIsInstance(self.bar.bar_counter.milk_bowl, MilkBowl)

    def test_back_room_threshold_state_is_object_only(self):
        self.assertIsInstance(self.bar.back_room.access, BackRoomAccess)
        self.assertIsInstance(self.bar.back_room.world_door, WorldDoor)
        self.assertIsInstance(self.bar.back_room.world_window, WorldWindow)
        self.assertIsInstance(self.bar.back_room.world_keypad, WorldKeypad)

    def test_staff_identity_and_policy_state_is_object_only(self):
        self.assertIsInstance(self.bar.bartender.origin, BarOrigin)
        self.assertIsInstance(self.bar.bouncer.origin, BarOrigin)
        self.assertIsInstance(
            self.bar.bouncer.principle_attributes,
            BouncerPrincipleAttributes,
        )
        self.assertIsInstance(self.bar.bouncer.cat_policy, CatEntryPolicy)
        self.bar.bartender.begin_shift(bar_day=1, shift_start_tick=2)
        self.assertIsInstance(self.bar.bartender.current_shift, BarShift)

    def test_dice_vial_physical_parts_are_objects(self):
        self.assertIsInstance(self.bar.dice_vial.container, DiceVialContainer)
        self.assertIsInstance(self.bar.dice_vial.medium, DiceVialMedium)
        self.assertIsInstance(self.bar.dice_vial.dice, DiceVialDie)

    def test_bar_signs_and_yard_objects_are_objects(self):
        self.assertIsInstance(self.bar.geometry_terminal.status_sign, GeometryStatusSign)
        self.assertIsInstance(self.bar.lemonade_signs.outside_sign, LemonadeSign)
        self.assertIsInstance(self.bar.lemonade_signs.inside_sign, LemonadeSign)
        from meeting_place.bar_yard import BarYard
        self.assertIsInstance(BarYard().lemon_tree, LemonTree)

    def test_cat_d20_box_is_object_when_created(self):
        self.universe.enable_quantum_layer()
        self.universe.boot_physics()
        # The normal bootstrap may attach cats later; use a minimal cat-like setup
        # only through the public manifestation API when available.
        from cats.cats import Cats
        if getattr(self.universe, "cats_layer", None) is None:
            self.universe.cats_layer = Cats(self.universe)
        cat = self.universe.cats_layer.create_cat(
            name="bar_object_state_d20",
            color="black",
            fur_length="short",
        )
        cat.special_traits.append("d20_cat")
        box = self.bar.place_cat_d20_box(cat)
        self.assertIsInstance(box, CatD20Box)

    def test_persistent_registries_remain_dictionaries(self):
        self.assertIsInstance(self.bar.drink_menu, dict)
        self.assertIsInstance(self.bar.new_drinks, dict)
        self.assertIsInstance(self.bar.guest_visit_history, dict)
        self.assertIsInstance(self.bar.back_room.bar_ingredients, dict)
        self.assertIsInstance(self.bar.how_to_mix_drinks.recipes, dict)
        self.assertIsInstance(self.bar.bartender.regular_drinks, dict)

    def test_domain_objects_do_not_expose_mapping_api(self):
        examples = [
            self.bar.bar_counter.milk_bowl,
            self.bar.back_room.world_door,
            self.bar.ambient_aroma,
            self.bar.permissions,
            self.bar.geometry_terminal.status_sign,
        ]
        for obj in examples:
            self.assertIsInstance(obj, ComponentObject)
            self.assertFalse(hasattr(obj, "get"))
            self.assertFalse(hasattr(obj, "keys"))
            with self.assertRaises(TypeError):
                _ = obj["state"]


if __name__ == "__main__":
    unittest.main()
