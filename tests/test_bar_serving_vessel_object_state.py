import unittest

from meeting_place.bar_counter import BarCounter
from meeting_place.bar_objects import (
    BarDrink,
    BarGlass,
    MilkBowl,
)
from meeting_place.bartender import Bartender


class BarServingVesselObjectStateTests(
    unittest.TestCase
):

    def test_glass_owns_filled_state(
        self
    ):
        glass = BarGlass(
            name="newton_glass",
            type="personal_bar_glass",
            owner="newton",
            state="clean",
            dirt=0.0,
            location="glass_shelf",
        )

        result = glass.fill(
            "singularity"
        )

        self.assertIs(
            result,
            glass
        )
        self.assertEqual(
            glass.state,
            "filled"
        )
        self.assertEqual(
            glass.contains,
            "singularity"
        )

        snapshot = glass.to_dict()

        self.assertEqual(
            snapshot[
                "contains"
            ],
            "singularity"
        )

        glass.empty()

        self.assertEqual(
            glass.state,
            "empty"
        )
        self.assertIsNone(
            glass.contains
        )

    def test_milk_bowl_uses_same_vessel_behavior(
        self
    ):
        bowl = MilkBowl(
            name="milk_bowl",
            type="bar_serving_object",
            state="empty",
            contains=None,
        )

        result = bowl.fill(
            "milk"
        )

        self.assertIs(
            result,
            bowl
        )
        self.assertEqual(
            bowl.state,
            "filled"
        )
        self.assertEqual(
            bowl.contains,
            "milk"
        )

    def test_bartender_pours_into_vessel_object(
        self
    ):
        counter = BarCounter()
        bartender = Bartender(
            counter.hidden_story_book
        )
        glass = BarGlass(
            name="newton_glass",
            type="personal_bar_glass",
            owner="newton",
            state="clean",
            dirt=0.0,
            location="glass_shelf",
        )
        drink = BarDrink(
            name="singularity",
            type="created_cocktail",
        )

        result = bartender.pour_drink(
            guest_name="newton",
            drink=drink,
            serving_object=glass,
        )

        self.assertIs(
            result,
            glass
        )
        self.assertEqual(
            glass.contains,
            "singularity"
        )
        self.assertEqual(
            glass.state,
            "filled"
        )

    def test_bartender_rejects_mapping_serving_bridge(
        self
    ):
        counter = BarCounter()
        bartender = Bartender(
            counter.hidden_story_book
        )
        drink = BarDrink(
            name="singularity",
            type="created_cocktail",
        )

        with self.assertRaises(
            AttributeError
        ):
            bartender.pour_drink(
                guest_name="newton",
                drink=drink,
                serving_object={
                    "name": "mapping_glass",
                    "state": "clean",
                },
            )


if __name__ == "__main__":
    unittest.main()
