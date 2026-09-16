import unittest

from cats.cat_bonding_system import CatBondingSystem
from cats.cat_components import CatBonds
from cats.cat_social_objects import CatBond
from cats.cats import Cats
from universe.universe import Universe


class CatBondRegistryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.first = self.cats.create_cat(
            name="first",
            color="black",
            fur_length="short",
        )
        self.second = self.cats.create_cat(
            name="second",
            color="white",
            fur_length="short",
        )
        self.system = CatBondingSystem(
            self.cats
        )

    def test_new_cat_has_object_bond_registry(self):
        self.assertIsInstance(
            self.first.bonds,
            CatBonds,
        )
        self.assertEqual(
            self.first.bonds.records,
            {},
        )

    def test_bond_is_stored_in_object_registry(self):
        self.system._store_bond(
            self.first,
            self.second,
            strength=0.8,
        )

        records = self.first.bonds.records

        self.assertIn(
            self.second.name,
            records,
        )
        self.assertIsInstance(
            records[self.second.name],
            CatBond,
        )

    def test_cats_own_separate_bond_registries(self):
        self.assertIsNot(
            self.first.bonds,
            self.second.bonds,
        )
        self.assertIsNot(
            self.first.bonds.records,
            self.second.bonds.records,
        )


if __name__ == "__main__":
    unittest.main()
