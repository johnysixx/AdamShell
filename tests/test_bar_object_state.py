import unittest
from dataclasses import FrozenInstanceError

from core.entity.domain_object import DomainObject
from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from meeting_place.terminals import BarTerminalDefinition
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

    def test_terminal_registry_contains_typed_objects(self):
        registry = self.bar.terminals.terminals

        expected = (
            "book_count_terminal",
            "book_search_terminal",
            "random_excerpt_terminal",
            "bar_story_count_terminal",
        )

        self.assertEqual(
            tuple(registry),
            expected,
        )

        for name in expected:
            terminal = registry[name]

            self.assertIsInstance(
                terminal,
                BarTerminalDefinition,
            )
            self.assertEqual(
                terminal.name,
                name,
            )
            self.assertTrue(terminal.type)
            self.assertTrue(terminal.purpose)

            for method in (
                "get",
                "keys",
                "items",
                "values",
                "__getitem__",
            ):
                self.assertFalse(
                    hasattr(terminal, method)
                )

            with self.assertRaises(TypeError):
                _ = terminal["type"]

        book_count = registry["book_count_terminal"]

        self.assertEqual(
            book_count.type,
            "display",
        )
        self.assertEqual(
            book_count.purpose,
            "show_library_book_count",
        )

        with self.assertRaises(FrozenInstanceError):
            book_count.purpose = "changed"

        with self.assertRaises(TypeError):
            BarTerminalDefinition(
                name="",
                type="display",
                purpose="invalid",
            )

    def test_terminal_snapshots_are_detached_from_objects(self):
        registry = self.bar.terminals.terminals
        terminal = registry["book_count_terminal"]

        self.assertIs(
            self.bar.state.terminals,
            registry,
        )

        first = self.bar.state.to_dict()
        second = self.bar.state.to_dict()

        world = self.universe.world[
            "meeting_place"
        ]

        self.assertEqual(
            first["terminals"]["book_count_terminal"],
            {
                "type": "display",
                "purpose": "show_library_book_count",
            },
        )

        first["terminals"]["book_count_terminal"][
            "purpose"
        ] = "changed"

        self.assertEqual(
            terminal.purpose,
            "show_library_book_count",
        )

        self.assertEqual(
            second["terminals"]["book_count_terminal"][
                "purpose"
            ],
            "show_library_book_count",
        )

        self.assertEqual(
            world["terminals"]["book_count_terminal"][
                "purpose"
            ],
            "show_library_book_count",
        )

        self.assertIs(
            registry["book_count_terminal"],
            terminal,
        )

        self.assertIsNot(
            first["terminals"]["book_count_terminal"],
            world["terminals"]["book_count_terminal"],
        )

    def test_terminal_registry_rejects_mapping_values(self):
        registry = self.bar.terminals.terminals
        original = registry["book_count_terminal"]

        try:
            registry["book_count_terminal"] = {
                "type": "display",
                "purpose": "legacy",
            }

            with self.assertRaises(TypeError):
                self.bar.state.to_dict()

        finally:
            registry["book_count_terminal"] = original

        self.assertIs(
            registry["book_count_terminal"],
            original,
        )

        self.assertEqual(
            self.bar.state.to_dict()["terminals"][
                "book_count_terminal"
            ]["purpose"],
            "show_library_book_count",
        )

        self.assertIs(
            self.bar.state.terminals,
            registry,
        )

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

    def test_cat_d20_box_rejects_mapping_atomically(self):
        before_box = getattr(self.bar, "cat_d20_box", None)
        world = self.universe.world["meeting_place"]
        before_present = "cat_d20_box" in world
        before_world_box = world.get("cat_d20_box")

        legacy = {
            "name": "legacy_cat_d20",
            "special_traits": ["d20_cat"],
        }

        with self.assertRaisesRegex(TypeError, "requires a cat"):
            self.bar.place_cat_d20_box(legacy)

        self.assertIs(
            getattr(self.bar, "cat_d20_box", None),
            before_box,
        )
        self.assertEqual(
            "cat_d20_box" in world,
            before_present,
        )
        self.assertIs(
            world.get("cat_d20_box"),
            before_world_box,
        )

    def test_persistent_registries_remain_dictionaries(self):
        self.assertIsInstance(self.bar.drink_menu, dict)
        self.assertIsInstance(self.bar.new_drinks, dict)
        self.assertIsInstance(self.bar.guest_visit_history, dict)
        self.assertIsInstance(self.bar.back_room.bar_ingredients, dict)
        self.assertIsInstance(self.bar.how_to_mix_drinks.recipes, dict)
        self.assertIsInstance(self.bar.bartender.regular_drinks, dict)

    def test_bar_objects_use_domain_object_equality(
        self
    ):
        first = BarOrigin(
            state="ready",
        )

        second = BarOrigin(
            state="ready",
        )

        other_type = BarShift(
            state="ready",
        )

        self.assertEqual(
            first,
            second,
        )

        self.assertNotEqual(
            first,
            other_type,
        )

        self.assertNotEqual(
            first,
            {
                "state": "ready",
            },
        )

    def test_domain_objects_do_not_expose_mapping_api(self):
        examples = [
            self.bar.bar_counter.milk_bowl,
            self.bar.back_room.world_door,
            self.bar.ambient_aroma,
            self.bar.permissions,
            self.bar.geometry_terminal.status_sign,
        ]
        for obj in examples:
            self.assertIsInstance(obj, DomainObject)
            self.assertFalse(hasattr(obj, "get"))
            self.assertFalse(hasattr(obj, "keys"))
            with self.assertRaises(TypeError):
                _ = obj["state"]


if __name__ == "__main__":
    unittest.main()
