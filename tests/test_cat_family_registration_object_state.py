import unittest

from cats.cat_family_registration_state import (
    CatFamilyRegistrationResult,
)
from cats.cat_family_system import (
    CatFamilySystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatFamilyRegistrationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.family = (
            CatFamilySystem(
                self.cats
            )
        )

        self.mother = (
            self.cats.create_cat(
                name="mother",
                color="black",
                fur_length="short",
            )
        )

        self.father = (
            self.cats.create_cat(
                name="father",
                color="orange",
                fur_length="short",
            )
        )

        self.kitten = (
            self.cats.create_cat(
                name="kitten",
                color="white",
                fur_length="short",
            )
        )

        self.kitten.father_name = (
            self.father.name
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

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "registered"
            ]

    def test_register_birth_returns_object(
        self
    ):
        result = (
            self.family.register_birth(
                mother=self.mother,
                kittens=[
                    self.kitten
                ],
                cats=self.cats.cats,
            )
        )

        self.assertIsInstance(
            result,
            CatFamilyRegistrationResult,
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.name,
            "cat_family_registered",
        )

        self.assertEqual(
            result.mother,
            self.mother.name,
        )

        self.assertEqual(
            result.kittens,
            (
                self.kitten.name,
            ),
        )

        self.assert_not_mapping(
            result
        )

    def test_registration_keeps_family_side_effects(
        self
    ):
        result = (
            self.family.register_birth(
                mother=self.mother,
                kittens=[
                    self.kitten
                ],
                cats=self.cats.cats,
            )
        )

        self.assertEqual(
            self.kitten
            .family
            .parents
            .mother,
            self.mother.name,
        )

        self.assertEqual(
            self.kitten
            .family
            .parents
            .father,
            self.father.name,
        )

        self.assertIn(
            self.kitten.name,
            self.mother.family.children,
        )

        self.assertIn(
            self.kitten.name,
            self.father.family.children,
        )

        self.assertEqual(
            result.kittens,
            (
                self.kitten.name,
            ),
        )

    def test_kittens_are_immutable_tuple(
        self
    ):
        second = (
            self.cats.create_cat(
                name="second",
                color="gray",
                fur_length="short",
            )
        )

        second.father_name = (
            self.father.name
        )

        result = (
            self.family.register_birth(
                mother=self.mother,
                kittens=[
                    self.kitten,
                    second,
                ],
                cats=self.cats.cats,
            )
        )

        self.assertIsInstance(
            result.kittens,
            tuple,
        )

        self.assertEqual(
            result.kittens,
            (
                "kitten",
                "second",
            ),
        )

        with self.assertRaises(
            AttributeError
        ):
            result.kittens.append(
                "third"
            )


if __name__ == "__main__":
    unittest.main()
