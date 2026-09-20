import unittest
from types import SimpleNamespace

from meeting_place.bar_counter import BarCounter
from meeting_place.bar_objects import BarDrink, BarGlass
from meeting_place.bartender import Bartender
from meeting_place.fridge import BarFridge


class BartenderServingObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.counter = BarCounter()
        self.bartender = Bartender(self.counter.hidden_story_book)
        self.drink = BarDrink(name="rum", type="basic_bar_drink")
        self.glass = BarGlass(
            name="guest_glass",
            type="personal_bar_glass",
            owner="guest",
            state="clean",
            dirt=0.0,
            location="bar_counter",
        )

    def assert_no_service_changes(self):
        self.assertEqual(self.bartender.regular_drinks, {})
        self.assertEqual(self.bartender.event_memory, [])
        self.assertEqual(self.glass.state, "clean")
        self.assertIsNone(self.glass.contains)

    def test_invalid_drinks_leave_service_state_unchanged(self):
        for method_name in ("pour_drink", "serve_without_order"):
            service = getattr(self.bartender, method_name)
            for drink in (
                self.drink.to_dict(),
                "rum",
                None,
                SimpleNamespace(name="rum"),
            ):
                with self.subTest(method=method_name, drink=drink):
                    with self.assertRaisesRegex(TypeError, "BarDrink"):
                        service("guest", drink, self.glass)

                    self.assert_no_service_changes()

    def test_mapping_vessel_is_rejected_before_order_is_remembered(self):
        for method_name in ("pour_drink", "serve_without_order"):
            service = getattr(self.bartender, method_name)
            vessel = {"name": "mapping_glass", "state": "clean"}

            with self.subTest(method=method_name):
                with self.assertRaisesRegex(TypeError, "BarServingVessel"):
                    service("guest", self.drink, vessel)

                self.assert_no_service_changes()
                self.assertEqual(vessel, {
                    "name": "mapping_glass", "state": "clean"
                })

    def test_prepared_drink_can_be_served_without_an_order(self):
        result = self.bartender.serve_without_order(
            "guest", self.drink, self.glass
        )

        self.assertIs(result, self.glass)
        self.assertEqual(self.glass.state, "filled")
        self.assertEqual(self.glass.contains, "rum")
        self.assertEqual(self.bartender.regular_drinks, {})
        self.assertEqual(self.bartender.event_memory, [
            "guest was served rum in guest_glass"
        ])

    def test_milk_inventory_is_served_without_remembering_an_order(self):
        milk = BarFridge().get_item("milk")
        bowl = self.counter.milk_bowl

        result = self.bartender.serve_without_order("cat", milk, bowl)

        self.assertIs(result, bowl)
        self.assertEqual(bowl.state, "filled")
        self.assertEqual(bowl.contains, "milk")
        self.assertEqual(milk.state, "cold")
        self.assertEqual(self.bartender.regular_drinks, {})
        self.assertEqual(self.bartender.event_memory, [
            "cat was served milk in milk_bowl"
        ])


if __name__ == "__main__":
    unittest.main()
