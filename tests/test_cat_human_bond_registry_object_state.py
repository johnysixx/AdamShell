import unittest

from cats.cat_components import CatHumanBond
from cats.cat_components import CatHumanBonds
from cats.cat_human_bond_system import CatHumanBondSystem
from cats.cats import Cats
from universe.universe import Universe


class Human:

    def __init__(self, name):
        self.name = name


class CatHumanBondRegistryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(self.universe)
        self.cat = self.cats.create_cat(
            name="bond_cat",
            color="black",
            fur_length="short",
        )
        self.human = Human("johny")
        self.system = CatHumanBondSystem(
            self.cats
        )

    def test_new_cat_has_object_human_bond_registry(self):
        self.assertIsInstance(
            self.cat.human_bonds,
            CatHumanBonds,
        )
        self.assertEqual(
            self.cat.human_bonds.records,
            {},
        )

    def test_interaction_stores_bond_in_registry(self):
        self.system.remember_interaction(
            self.cat,
            self.human,
            positive=True,
            significance=0.1,
        )

        records = self.cat.human_bonds.records

        self.assertIn(
            self.human.name,
            records,
        )
        self.assertIsInstance(
            records[self.human.name],
            CatHumanBond,
        )

    def test_cats_own_separate_human_bond_registries(self):
        other = self.cats.create_cat(
            name="other_cat",
            color="white",
            fur_length="short",
        )

        self.assertIsNot(
            self.cat.human_bonds,
            other.human_bonds,
        )
        self.assertIsNot(
            self.cat.human_bonds.records,
            other.human_bonds.records,
        )


if __name__ == "__main__":
    unittest.main()
