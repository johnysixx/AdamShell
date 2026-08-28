import unittest

from universe.universe import Universe
from universe.bootstraps.entity_bootstrap import EntityBootstrap


class SharedCatsLayerTests(unittest.TestCase):

    def test_bootstrap_and_manifestation_share_one_cats_layer(self):
        universe = Universe()

        bootstrap = EntityBootstrap(
            universe,
            None,
            None
        )

        bootstrap._create_pazuzu()

        original_layer = universe.cats_layer

        universe.manifest_cat(
            name="second_cat",
            source="test"
        )

        self.assertIs(
            universe.cats_layer,
            original_layer
        )

        self.assertIs(
            bootstrap.cats,
            universe.cats_layer
        )

        self.assertEqual(
            len(universe.cats_layer.cats),
            2
        )

        names = [
            cat.name
            for cat in universe.cats_layer.cats
        ]

        self.assertIn(
            "pazuzu",
            names
        )

        self.assertIn(
            "second_cat",
            names
        )


if __name__ == "__main__":
    unittest.main()