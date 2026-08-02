import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import UniverseBootstrap
from universe.bootstraps.entity_bootstrap import EntityBootstrap


class CatD20ArrivalTests(unittest.TestCase):

    def test_cat_d20_arrives_drinks_milk_and_enters_box(self):
        registry = UniverseRegistry()
        universe = Universe()

        (
            root_transition,
            layers,
            idea_universe
        ) = UniverseBootstrap(
            registry,
            universe
        ).run()

        EntityBootstrap(
            universe,
            idea_universe,
            root_transition
        ).run()

        bar = layers.get("meeting")

        result = bar.welcome_cat_d20()

        cat = result["cat"]
        box = result["box"]

        self.assertTrue(
            result["created"]
        )

        self.assertEqual(
            cat["type"],
            "cat"
        )

        self.assertIn(
            "d20_cat",
            cat["special_traits"]
        )

        self.assertEqual(
            cat["state"],
            "resting_in_cat_d20_box"
        )

        self.assertFalse(
            cat["cat_d20"]["is_die"]
        )

        self.assertFalse(
            cat["cat_d20"]["can_be_thrown"]
        )

        self.assertTrue(
            bar.bartender.knows_guest(
                cat["name"]
            )
        )

        self.assertIn(
            cat,
            bar.entities
        )

        self.assertEqual(
            bar.bar_counter.milk_bowl[
                "contains"
            ],
            "milk"
        )

        self.assertEqual(
            box["occupied_by"],
            cat["name"]
        )

        self.assertEqual(
            box["location"],
            "on_bar_counter"
        )

        self.assertIs(
            universe.world[
                "meeting_place"
            ]["cat_d20_box"],
            box
        )

    def test_second_welcome_does_not_create_duplicate(self):
        registry = UniverseRegistry()
        universe = Universe()

        (
            root_transition,
            layers,
            idea_universe
        ) = UniverseBootstrap(
            registry,
            universe
        ).run()

        EntityBootstrap(
            universe,
            idea_universe,
            root_transition
        ).run()

        bar = layers.get("meeting")

        first = bar.welcome_cat_d20()
        second = bar.welcome_cat_d20()

        self.assertTrue(
            first["created"]
        )

        self.assertFalse(
            second["created"]
        )

        self.assertIs(
            first["cat"],
            second["cat"]
        )

        cat_d20_count = sum(
            1
            for cat in universe.cats_layer.cats
            if cat["name"] == "cat_d20"
        )

        self.assertEqual(
            cat_d20_count,
            1
        )


if __name__ == "__main__":
    unittest.main()