import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap
)


class CatD20PazuzuCanonTests(unittest.TestCase):

    def test_cat_d20_is_first_and_prepares_pazuzu(self):
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

        bar = layers.get(
            "meeting"
        )

        arrival = (
            bar.welcome_cat_d20()
        )

        prepared = (
            bar.cat_d20_prepare_pazuzu_profile()
        )

        bootstrap = EntityBootstrap(
            universe,
            idea_universe,
            root_transition,
            pazuzu_profile=prepared[
                "profile"
            ]
        )

        bootstrap._create_pazuzu()

        names = [
            cat.name
            for cat in universe.cats_layer.cats
        ]

        self.assertEqual(
            names,
            [
                "cat_d20",
                "pazuzu"
            ]
        )

        self.assertIs(
            universe.cats_layer.cats[0],
            arrival["cat"]
        )

        self.assertIs(
            universe.cats_layer.cats[1],
            bootstrap.pazuzu
        )

        self.assertEqual(
            bootstrap.pazuzu.color,
            "black"
        )

        self.assertEqual(
            bootstrap.pazuzu.fur_length,
            "short"
        )

        self.assertEqual(
            bootstrap.pazuzu.pattern,
            "solid"
        )

        self.assertEqual(
            bootstrap.pazuzu.eye_color,
            "green"
        )

        self.assertEqual(
            bootstrap.pazuzu.sex,
            "female"
        )

        self.assertTrue(
            prepared["prepared"]
        )

        self.assertFalse(
            prepared["random"]
        )

        self.assertEqual(
            prepared["mode"],
            "canonical_turn"
        )


if __name__ == "__main__":
    unittest.main()