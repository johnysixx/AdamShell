import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.feline_wisdom import FelineWisdom
from cats.feline_ability_resolver import (
    FelineAbilityResolver,
)
from cats.feline_wisdom_state import (
    FelineHumanDoorCapabilityResult,
)


class FelineHumanDoorCapabilityObjectStateTests(
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

        self.kitten = (
            self.cats.create_cat(
                name="kitten",
                color="white",
                fur_length="short",
                origin="kitten_birth_resolver",
            )
        )

        self.resolver.register_pazuzu_door_method(
            self.pazuzu
        )

    def give_kitten_handle_method(
        self
    ):
        return (
            FelineWisdom.learn_ability_method(
                cat=self.kitten,
                ability_name=(
                    "open_human_door"
                ),
                method_name=(
                    "hang_on_handle"
                ),
                teacher_name=(
                    self.pazuzu.name
                ),
                constraints={
                    "requires_unlocked": True,
                    "opens_toward_cat": True,
                    "opens_away_from_cat": True,
                    "can_close": False,
                },
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
            "to_dict",
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
                "allowed"
            ]

    def test_unlearned_open_result_is_object(
        self
    ):
        result = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=False,
                opens_toward_cat=True,
            )
        )

        self.assertIsInstance(
            result,
            FelineHumanDoorCapabilityResult,
        )

        self.assertFalse(
            result.allowed
        )

        self.assertEqual(
            result.action,
            "open",
        )

        self.assertEqual(
            result.reason,
            "human_door_ability_not_learned",
        )

        self.assertEqual(
            result.usable_methods,
            (),
        )

        self.assert_not_mapping(
            result
        )

    def test_open_result_keeps_methods_as_tuple(
        self
    ):
        self.give_kitten_handle_method()

        result = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=False,
                opens_toward_cat=True,
            )
        )

        self.assertTrue(
            result.allowed
        )

        self.assertEqual(
            result.reason,
            "door_can_be_opened",
        )

        self.assertEqual(
            result.usable_methods,
            (
                "hang_on_handle",
            ),
        )

        self.assert_not_mapping(
            result
        )

        self.assertEqual(
            result.usable_methods,
            (
                "hang_on_handle",
            ),
        )

    def test_locked_open_result_is_object(
        self
    ):
        self.give_kitten_handle_method()

        result = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=True,
                opens_toward_cat=True,
            )
        )

        self.assertFalse(
            result.allowed
        )

        self.assertEqual(
            result.reason,
            "door_is_locked",
        )

        self.assert_not_mapping(
            result
        )

    def test_close_result_is_object(
        self
    ):
        result = (
            self.resolver
            .can_close_human_door(
                self.pazuzu
            )
        )

        self.assertIsInstance(
            result,
            FelineHumanDoorCapabilityResult,
        )

        self.assertFalse(
            result.allowed
        )

        self.assertEqual(
            result.action,
            "close",
        )

        self.assertEqual(
            result.reason,
            "no_cat_knows_how_to_close_human_doors",
        )

        self.assert_not_mapping(
            result
        )


if __name__ == "__main__":
    unittest.main()
