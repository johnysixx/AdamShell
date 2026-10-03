import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.feline_ability_method_state import (
    FelineAbilityMethodState,
)
from cats.feline_ability_resolver import (
    FelineAbilityResolver,
)
from cats.feline_wisdom_state import (
    FelineAbilityMethodRegistrationResult,
    FelineTeachingAbilitiesRegistrationResult,
)


class FelineAbilityMethodRegistrationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.resolver = (
            FelineAbilityResolver(
                self.universe
            )
        )

        self.pazuzu = (
            self.cats.create_cat(
                name="pazuzu",
                color="black",
                fur_length="short",
                origin="canonical_birth",
            )
        )

        self.queen = (
            self.cats.create_cat(
                name="queen_elisabeth",
                color="calico",
                fur_length="long",
                origin="canonical_birth",
            )
        )

        self.garfield = (
            self.cats.create_cat(
                name="garfield",
                color="orange",
                fur_length="short",
                origin="canonical_birth",
            )
        )

    def assert_not_mapping(
        self,
        result,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "method"
            ]

    def test_pazuzu_registration_returns_method_object(
        self
    ):
        result = (
            self.resolver
            .register_pazuzu_door_method(
                self.pazuzu
            )
        )

        self.assertIsInstance(
            result,
            FelineAbilityMethodRegistrationResult,
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.cat,
            "pazuzu",
        )

        self.assertEqual(
            result.ability,
            "open_human_door",
        )

        self.assertIsInstance(
            result.method,
            FelineAbilityMethodState,
        )

        stored = (
            self.pazuzu
            .feline_wisdom
            .abilities[
                "open_human_door"
            ]
            .methods[
                "hang_on_handle"
            ]
        )

        self.assertIs(
            result.method,
            stored,
        )

        self.assert_not_mapping(
            result
        )

        boundary = (
            result.to_dict()
        )

        boundary[
            "method"
        ][
            "constraints"
        ][
            "can_close"
        ] = True

        self.assertFalse(
            result.method
            .constraints[
                "can_close"
            ]
        )

    def test_garfield_registration_returns_two_method_objects(
        self
    ):
        result = (
            self.resolver
            .register_garfield_teaching_abilities(
                self.garfield
            )
        )

        self.assertIsInstance(
            result,
            FelineTeachingAbilitiesRegistrationResult,
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.cat,
            "garfield",
        )

        teach_stored = (
            self.garfield
            .feline_wisdom
            .abilities[
                "teach_other_cats"
            ]
            .methods[
                "garfield_teaching_method"
            ]
        )

        meta_stored = (
            self.garfield
            .feline_wisdom
            .abilities[
                "teach_teaching"
            ]
            .methods[
                "garfield_meta_teaching_method"
            ]
        )

        self.assertIs(
            result.teach_other_cats,
            teach_stored,
        )

        self.assertIs(
            result.teach_teaching,
            meta_stored,
        )

        self.assert_not_mapping(
            result
        )

        boundary = (
            result.to_dict()
        )

        boundary[
            "teach_other_cats"
        ][
            "constraints"
        ][
            "can_teach_meow"
        ] = False

        self.assertTrue(
            result.teach_other_cats
            .constraints[
                "can_teach_meow"
            ]
        )

        audit = (
            self.resolver
            .history[-1]
        )

        self.assertIsInstance(
            audit,
            dict,
        )

        self.assertTrue(
            audit[
                "registered"
            ]
        )

        audit[
            "teach_teaching"
        ][
            "constraints"
        ][
            "can_teach_teach_teaching"
        ] = False

        self.assertTrue(
            result.teach_teaching
            .constraints[
                "can_teach_teach_teaching"
            ]
        )

    def test_queen_registration_returns_method_object(
        self
    ):
        result = (
            self.resolver
            .register_queen_elisabeth_door_method(
                self.queen
            )
        )

        self.assertIsInstance(
            result,
            FelineAbilityMethodRegistrationResult,
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.cat,
            "queen_elisabeth",
        )

        self.assertEqual(
            result.method.name,
            "pull_with_paw",
        )

        stored = (
            self.queen
            .feline_wisdom
            .abilities[
                "open_human_door"
            ]
            .methods[
                "pull_with_paw"
            ]
        )

        self.assertIs(
            result.method,
            stored,
        )

        self.assert_not_mapping(
            result
        )


if __name__ == "__main__":
    unittest.main()
