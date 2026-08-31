import unittest
from types import SimpleNamespace

from meeting_place.bar_objects import BarDrink
from meeting_place.meeting_place import MeetingPlace
from multiverse import UniverseRegistry
from universe.universe import Universe


class BarDrinkObjectStateTests(unittest.TestCase):

    def _meeting_place(self):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()
        return MeetingPlace(universe)

    def test_served_drinks_are_domain_objects(self):
        bar = self._meeting_place()
        guest = SimpleNamespace(
            name="guest",
            type="human",
        )

        result = bar.serve_basic_drinks_on_tab(
            entity=guest,
            drink_names=["wine", "beer"],
        )

        self.assertTrue(
            all(
                isinstance(drink, BarDrink)
                for drink in result["drinks"]
            )
        )

        self.assertEqual(
            [drink.name for drink in result["drinks"]],
            ["wine", "beer"],
        )

    def test_drink_objects_have_no_mapping_api(self):
        drink = BarDrink(
            name="rum",
            type="basic_bar_drink",
            category="basic_drink",
        )

        for name in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
        ):
            self.assertFalse(
                hasattr(drink, name),
                name,
            )

        with self.assertRaises(TypeError):
            _ = drink["name"]

    def test_receipt_remains_boundary_snapshot(self):
        bar = self._meeting_place()
        guest = SimpleNamespace(
            name="guest",
            type="human",
        )

        result = bar.serve_basic_drinks_on_tab(
            entity=guest,
            drink_names=["wine"],
        )

        self.assertIsInstance(
            result["receipt"],
            dict,
        )
        self.assertIsInstance(
            result["receipt"]["items"][0],
            dict,
        )

    def test_public_snapshot_is_detached_from_drink(self):
        drink = BarDrink(
            name="lilith",
            type="learned_bar_drink",
            effects={"energy_j": 1.0},
            garnish={"ingredient": "lemon"},
        )

        snapshot = drink.to_dict()
        snapshot["effects"]["energy_j"] = 9.0
        snapshot["garnish"]["ingredient"] = "lime"

        self.assertEqual(
            drink.effects["energy_j"],
            1.0,
        )
        self.assertEqual(
            drink.garnish["ingredient"],
            "lemon",
        )


if __name__ == "__main__":
    unittest.main()
