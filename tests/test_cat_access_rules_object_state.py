import unittest
from dataclasses import FrozenInstanceError, replace

from cats.cat_access_rules import CatAccessRules
from cats.cats import Cats
from universe.universe import Universe


class CatAccessRulesObjectStateTests(
    unittest.TestCase
):

    def test_access_rules_are_deeply_immutable(self):
        rules = CatAccessRules()

        self.assertTrue(
            rules.can_access_anywhere,
        )

        self.assertEqual(
            rules.access_via,
            ("boxes", "cat_doors"),
        )

        self.assertIsInstance(
            rules.access_via,
            tuple,
        )

        self.assertFalse(
            hasattr(rules, "__dict__"),
        )

        for method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(rules, method)
            )

        with self.assertRaises(TypeError):
            _ = rules["access_via"]

        with self.assertRaises(FrozenInstanceError):
            rules.can_access_anywhere = False

        with self.assertRaises(FrozenInstanceError):
            rules.access_via = ("boxes",)

        self.assertFalse(
            hasattr(rules.access_via, "append")
        )

    def test_access_rules_reject_mutable_or_invalid_values(self):
        with self.assertRaises(TypeError):
            CatAccessRules(
                access_via=["boxes", "cat_doors"],
            )

        with self.assertRaises(TypeError):
            CatAccessRules(
                can_access_anywhere="yes",
            )

        with self.assertRaises(TypeError):
            CatAccessRules(
                access_via=("boxes", None),
            )

        with self.assertRaises(TypeError):
            CatAccessRules(
                access_via=("",),
            )

        restricted = CatAccessRules(
            can_access_anywhere=False,
            access_via=("boxes",),
        )

        self.assertFalse(
            restricted.can_access_anywhere,
        )

        self.assertEqual(
            restricted.access_via,
            ("boxes",),
        )

    def test_shared_rules_and_public_boundary_are_preserved(self):
        universe = Universe()
        cats = Cats(universe)

        cat = cats.create_cat(
            name="immutable_access_cat",
            color="black",
            fur_length="short",
        )

        original = cats.access_rules

        self.assertIs(
            cat.access,
            original,
        )

        self.assertTrue(
            cats.can_travel(cat, via="boxes"),
        )

        self.assertTrue(
            cats.can_travel(cat, via="cat_doors"),
        )

        self.assertFalse(
            cats.can_travel(cat, via="unknown_method"),
        )

        restricted = replace(
            original,
            can_access_anywhere=False,
        )

        self.assertIsNot(
            restricted,
            original,
        )

        self.assertFalse(
            restricted.can_access_anywhere,
        )

        self.assertTrue(
            original.can_access_anywhere,
        )

        snapshot = cats.public_state["access_rules"]

        self.assertEqual(
            snapshot,
            {
                "can_access_anywhere": True,
                "access_via": [
                    "boxes",
                    "cat_doors",
                ],
            },
        )

        snapshot["access_via"].append("changed")

        self.assertEqual(
            original.access_via,
            ("boxes", "cat_doors"),
        )

        self.assertIs(
            cat.access,
            cats.access_rules,
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatAccessRules()

        self.assertTrue(
            state.can_access_anywhere
        )

        self.assertEqual(
            state.access_via,
            (
                "boxes",
                "cat_doors",
            ),
        )

        self.assertFalse(
            hasattr(
                state,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                state,
                "__getitem__",
            )
        )

        self.assertFalse(
            hasattr(
                state,
                "__setitem__",
            )
        )

        self.assertFalse(
            hasattr(
                state,
                "to_dict",
            )
        )

    def test_created_cat_shares_species_access_rules(
        self
    ):
        universe = Universe()
        cats = Cats(universe)

        cat = cats.create_cat(
            name="access_cat",
            color="black",
            fur_length="short",
        )

        self.assertIs(
            cat.access,
            cats.access_rules,
        )

        self.assertIsInstance(
            cat.access,
            CatAccessRules,
        )

    def test_public_state_serializes_access_rules(
        self
    ):
        universe = Universe()
        cats = Cats(universe)

        boundary = (
            cats.public_state[
                "access_rules"
            ]
        )

        self.assertIsInstance(
            boundary,
            dict,
        )

        self.assertEqual(
            boundary,
            {
                "can_access_anywhere": True,
                "access_via": [
                    "boxes",
                    "cat_doors",
                ],
            },
        )

        boundary[
            "access_via"
        ].append(
            "changed"
        )

        self.assertNotIn(
            "changed",
            cats.access_rules.access_via,
        )

    def test_legacy_mapping_rules_are_rejected(
        self
    ):
        universe = Universe()
        cats = Cats(universe)

        cat = cats.create_cat(
            name="legacy_access_cat",
            color="black",
            fur_length="short",
        )

        cats.cats_state.access_rules = {
            "can_access_anywhere": True,
            "access_via": [
                "boxes"
            ],
        }

        with self.assertRaises(
            TypeError
        ):
            cats.can_travel(
                cat,
                via="boxes",
            )


if __name__ == "__main__":
    unittest.main()
