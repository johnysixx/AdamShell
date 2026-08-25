import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace


class BarIngredientsTests(unittest.TestCase):

    def test_bar_has_basic_rum_from_start(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        self.assertIn(
            "rum",
            meeting_place.back_room.bar_ingredients
        )

        self.assertTrue(
            meeting_place.back_room.bar_ingredients[
                "rum"
            ]["available"]
        )

        self.assertTrue(
            meeting_place.back_room.bar_ingredients[
                "rum"
            ]["fundamental"]
        )


    def test_bar_starts_with_rum_but_without_liquid_hydrocarbons(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        self.assertIn(
            "rum",
            meeting_place.back_room.bar_ingredients
        )

        self.assertTrue(
            meeting_place.back_room.bar_ingredients[
                "rum"
            ]["available"]
        )

        self.assertNotIn(
            "liquid_hydrocarbons",
            meeting_place.back_room.bar_ingredients
        )


    def test_bar_can_stock_liquid_hydrocarbons_after_they_exist(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        self.assertNotIn(
            "liquid_hydrocarbons",
            meeting_place
            .back_room
            .bar_ingredients
        )

        universe.liquid_hydrocarbons = True

        meeting_place.refresh_bar_ingredients()

        self.assertIn(
            "liquid_hydrocarbons",
            meeting_place
            .back_room
            .bar_ingredients
        )

        self.assertTrue(
            meeting_place
            .back_room
            .bar_ingredients[
                "liquid_hydrocarbons"
            ]["available"]
        )


    def test_raspberry_rum_is_available_only_after_liquid_hydrocarbons_exist(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        self.assertNotIn(
            "raspberry_rum",
            meeting_place.drink_menu
        )

        universe.liquid_hydrocarbons = True

        meeting_place.refresh_bar_ingredients()

        meeting_place.refresh_basic_drinks()

        self.assertIn(
            "raspberry_rum",
            meeting_place.drink_menu
        )


    def test_liquid_hydrocarbons_start_with_two_hundred_shots(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        universe.liquid_hydrocarbons = True

        meeting_place.refresh_bar_ingredients()

        stock = (
            meeting_place
            .back_room
            .bar_ingredients[
                "liquid_hydrocarbons"
            ]
        )

        self.assertEqual(
            stock["shots"],
            200
        )


    def test_mixing_raspberry_rum_consumes_one_hydrocarbon_shot(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        universe.liquid_hydrocarbons = True
        meeting_place.refresh_bar_ingredients()

        stock = (
            meeting_place
            .back_room
            .bar_ingredients[
                "liquid_hydrocarbons"
            ]
        )

        self.assertEqual(
            stock["shots"],
            200
        )

        meeting_place.mix_basic_drink(
            "raspberry_rum"
        )

        self.assertEqual(
            stock["shots"],
            199
        )


    def test_basic_drink_constructor_consumes_recipe_ingredients(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        universe.liquid_hydrocarbons = True
        meeting_place.refresh_bar_ingredients()

        stock = (
            meeting_place
            .back_room
            .bar_ingredients[
                "liquid_hydrocarbons"
            ]
        )

        self.assertEqual(
            stock["shots"],
            200
        )

        drink = meeting_place.mix_basic_drink(
            "raspberry_rum"
        )

        self.assertEqual(
            stock["shots"],
            199
        )

        self.assertEqual(
            drink["name"],
            "raspberry_rum"
        )


    def test_empty_bar_ingredient_creates_cronenberg(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        universe.liquid_hydrocarbons = True
        meeting_place.refresh_bar_ingredients()

        meeting_place.back_room.bar_ingredients[
            "liquid_hydrocarbons"
        ]["shots"] = 0

        cronenberg_count_before = len(
            universe.cronenbergs
        )

        meeting_place.mix_basic_drink(
            "raspberry_rum"
        )

        self.assertEqual(
            len(
                universe.cronenbergs
            ),
            cronenberg_count_before + 1
        )

        cronenberg = universe.cronenbergs[-1]

        self.assertEqual(
            cronenberg.type,
            "cronenberg"
        )

        self.assertEqual(
            cronenberg.traits.source_component,
            "meeting_place"
        )

        self.assertEqual(
            cronenberg.traits.source_operation,
            "mix_basic_drink"
        )


    def test_last_hydrocarbon_shot_is_served_before_cronenberg(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        universe.liquid_hydrocarbons = True
        meeting_place.refresh_bar_ingredients()

        stock = (
            meeting_place
            .back_room
            .bar_ingredients[
                "liquid_hydrocarbons"
            ]
        )

        stock["shots"] = 1

        cronenberg_count_before = len(
            universe.cronenbergs
        )

        drink = meeting_place.mix_basic_drink(
            "raspberry_rum"
        )

        self.assertEqual(
            drink["name"],
            "raspberry_rum"
        )

        self.assertEqual(
            stock["shots"],
            0
        )

        self.assertEqual(
            len(universe.cronenbergs),
            cronenberg_count_before
        )

        result = meeting_place.mix_basic_drink(
            "raspberry_rum"
        )

        self.assertEqual(
            stock["shots"],
            0
        )

        self.assertEqual(
            len(universe.cronenbergs),
            cronenberg_count_before + 1
        )

        self.assertEqual(
            result.type,
            "cronenberg"
        )


if __name__ == "__main__":
    unittest.main()









