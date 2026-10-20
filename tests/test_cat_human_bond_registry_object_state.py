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

    def test_new_cat_has_object_human_bond_registry(
        self
    ):
        registry = (
            self.cat.human_bonds
        )

        self.assertIsInstance(
            registry,
            CatHumanBonds,
        )

        self.assertTrue(
            registry.is_empty
        )

        self.assertEqual(
            registry.count,
            0,
        )

        self.assertEqual(
            registry.records(),
            (),
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "pop",
            "setdefault",
            "__getitem__",
            "__setitem__",
            "__contains__",
        ):
            self.assertFalse(
                hasattr(
                    registry,
                    mapping_method,
                )
            )

    def test_interaction_stores_bond_in_registry(
        self
    ):
        self.system.remember_interaction(
            self.cat,
            self.human,
            positive=True,
            significance=0.1,
        )

        registry = (
            self.cat.human_bonds
        )

        bond = registry.record(
            self.human.name
        )

        self.assertEqual(
            registry.count,
            1,
        )

        self.assertIsInstance(
            bond,
            CatHumanBond,
        )

        self.assertEqual(
            bond.human,
            self.human.name,
        )

        with self.assertRaises(
            TypeError
        ):
            registry.store({
                "human": self.human.name,
            })

    def test_cats_own_separate_human_bond_registries(
        self
    ):
        other = self.cats.create_cat(
            name="other_cat",
            color="white",
            fur_length="short",
        )

        self.assertIsNot(
            self.cat.human_bonds,
            other.human_bonds,
        )

        self.system.remember_interaction(
            self.cat,
            self.human,
            positive=True,
            significance=0.1,
        )

        self.assertEqual(
            self.cat.human_bonds.count,
            1,
        )

        self.assertTrue(
            other.human_bonds.is_empty
        )


if __name__ == "__main__":
    unittest.main()
