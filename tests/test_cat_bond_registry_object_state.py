import unittest

from cats.cat_bonding_system import CatBondingSystem
from cats.cat_components import CatBonds
from cats.cat_social_objects import CatBond
from cats.cats import Cats
from core.entity.domain_object import DomainObject
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

    def test_new_cat_has_object_bond_registry(
        self
    ):
        registry = (
            self.first.bonds
        )

        self.assertIsInstance(
            registry,
            CatBonds,
        )

        self.assertIsInstance(
            registry,
            DomainObject,
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

        self.assertFalse(
            hasattr(
                registry,
                "to_dict",
            )
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

    def test_bond_is_stored_in_object_registry(
        self
    ):
        self.system._store_bond(
            self.first,
            self.second,
            strength=0.8,
        )

        registry = (
            self.first.bonds
        )

        bond = registry.record(
            self.second.name
        )

        self.assertEqual(
            registry.count,
            1,
        )

        self.assertIsInstance(
            bond,
            CatBond,
        )

        self.assertEqual(
            bond.other_cat,
            self.second.name,
        )

        with self.assertRaises(
            TypeError
        ):
            registry.store({
                "other_cat": self.second.name,
            })

    def test_cats_own_separate_bond_registries(
        self
    ):
        self.assertIsNot(
            self.first.bonds,
            self.second.bonds,
        )

        self.system._store_bond(
            self.first,
            self.second,
            strength=0.8,
        )

        self.assertEqual(
            self.first.bonds.count,
            1,
        )

        self.assertTrue(
            self.second.bonds.is_empty
        )


if __name__ == "__main__":
    unittest.main()
