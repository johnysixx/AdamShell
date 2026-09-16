import unittest

from cats.cat_components import CatTerritories
from cats.cat_social_objects import CatTerritoryClaim
from cats.cat_territory_system import CatTerritorySystem
from cats.cats import Cats
from universe.universe import Universe


class CatTerritoriesObjectStateTests(unittest.TestCase):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(
            name="territory_cat",
            color="black",
            fur_length="short",
        )
        self.cat.current_layer = "meeting_place"
        self.cat.location = "window"
        self.system = CatTerritorySystem(
            self.cats
        )

    def test_new_cat_has_object_territory_registry(self):
        self.assertIsInstance(
            self.cat.territories,
            CatTerritories,
        )
        self.assertEqual(
            self.cat.territories.claims,
            {},
        )

    def test_claim_is_stored_in_object_registry(self):
        claim = self.system.claim(
            self.cat,
            strength=0.7,
        )
        key = "meeting_place::window"

        self.assertIn(
            key,
            self.cat.territories.claims,
        )
        self.assertIsInstance(
            self.cat.territories.claims[key],
            CatTerritoryClaim,
        )
        self.assertEqual(
            claim,
            self.cat.territories.claims[key],
        )

    def test_scent_mark_updates_registered_claim(self):
        self.system.claim(
            self.cat,
            strength=0.6,
        )
        self.system.scent_mark(
            self.cat
        )

        claim = self.cat.territories.claims[
            "meeting_place::window"
        ]

        self.assertEqual(
            claim.scent_marks,
            2,
        )
        self.assertGreater(
            claim.strength,
            0.6,
        )


if __name__ == "__main__":
    unittest.main()
