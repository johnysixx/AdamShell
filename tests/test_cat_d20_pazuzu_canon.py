import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from universe.bootstraps.universe_bootstrap import (
    UniverseBootstrap
)
from universe.bootstraps.entity_bootstrap import (
    EntityBootstrap
)
from meeting_place.bar_objects import (
    CatD20CanonicalProfilePreparedEvent,
    CatD20Profile,
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
            pazuzu_profile=prepared.profile
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
            arrival.cat
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

        self.assertIsInstance(
            prepared,
            CatD20CanonicalProfilePreparedEvent,
        )

        self.assertIsInstance(
            prepared.profile,
            CatD20Profile,
        )

        self.assertIsInstance(
            bootstrap.pazuzu_profile,
            CatD20Profile,
        )

        self.assertIsNot(
            bootstrap.pazuzu_profile,
            prepared.profile,
        )

        self.assertTrue(
            prepared.prepared
        )

        self.assertFalse(
            prepared.random
        )

        self.assertEqual(
            prepared.mode,
            "canonical_turn"
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    prepared,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = prepared[
                "profile"
            ]


if __name__ == "__main__":
    unittest.main()