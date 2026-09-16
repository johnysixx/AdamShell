import unittest

from cats.cat_bonding_system import CatBondingSystem
from cats.cat_social_objects import CatBond
from cats.cats import Cats
from universe.universe import Universe


class CatBondObjectStateTests(unittest.TestCase):

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

    def _store_bond(self):
        self.system._store_bond(
            self.first,
            self.second,
            strength=0.8,
        )
        return self.first.bonds.records[
            self.second.name
        ]

    def test_stored_bond_is_object(self):
        bond = self._store_bond()

        self.assertIsInstance(
            bond,
            CatBond,
        )
        self.assertTrue(
            bond.active
        )
        self.assertEqual(
            bond.other_cat,
            self.second.name,
        )

    def test_bond_strength_is_object_state(self):
        bond = self._store_bond()

        self.system._strengthen(
            self.first,
            self.second,
            amount=0.1,
        )

        self.assertAlmostEqual(
            bond.strength,
            0.9,
        )

    def test_object_bond_is_recognized(self):
        self._store_bond()

        self.assertTrue(
            self.system.is_bonded(
                self.first,
                self.second,
            )
        )


if __name__ == "__main__":
    unittest.main()
