import unittest

from cats.cat_access_rules import CatAccessRules
from cats.cats import Cats
from universe.universe import Universe


class CatAccessRulesObjectStateTests(
    unittest.TestCase
):

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatAccessRules()

        self.assertTrue(
            state.can_access_anywhere
        )

        self.assertEqual(
            state.access_via,
            [
                "boxes",
                "cat_doors",
            ],
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
