import unittest

from cats.cat_family_system import CatFamilySystem
from cats.cat_parentage_state import (
    CatParentageState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatParentageObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.family = CatFamilySystem(
            self.cats
        )

        self.mother = (
            self.cats.create_cat(
                name='parentage_mother',
                color='black',
                fur_length='short',
            )
        )

        self.kitten = (
            self.cats.create_cat(
                name='parentage_kitten',
                color='white',
                fur_length='short',
            )
        )

    def test_parentage_has_no_mapping_api(
        self
    ):
        state = CatParentageState(
            mother='mother',
            father='father',
        )

        self.assertEqual(
            state.mother,
            'mother',
        )

        self.assertEqual(
            state.father,
            'father',
        )

        self.assertFalse(
            hasattr(
                state,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__getitem__',
            )
        )

        self.assertFalse(
            hasattr(
                state,
                '__setitem__',
            )
        )

    def test_cat_family_starts_with_parentage_object(
        self
    ):
        self.assertIsInstance(
            self.kitten.family.parents,
            CatParentageState,
        )

        self.assertIsNone(
            self.kitten.family.parents.mother
        )

        self.assertIsNone(
            self.kitten.family.parents.father
        )

        self.assertFalse(
            hasattr(
                self.kitten,
                'parents',
            )
        )

    def test_register_birth_mutates_same_parentage_object(
        self
    ):
        state = (
            self.kitten.family.parents
        )

        self.kitten.father_name = None

        self.family.register_birth(
            mother=self.mother,
            kittens=[self.kitten],
            cats=self.cats.cats,
        )

        self.assertIs(
            self.kitten.family.parents,
            state,
        )

        self.assertEqual(
            state.mother,
            self.mother.name,
        )

        self.assertIsNone(
            state.father
        )

    def test_legacy_parentage_mapping_is_rejected(
        self
    ):
        self.kitten.family.parents = {
            'mother': self.mother.name,
            'father': None,
        }

        with self.assertRaises(
            TypeError
        ):
            self.family.relation(
                self.kitten,
                self.mother,
            )

    def test_role_lookup_is_explicit(
        self
    ):
        state = CatParentageState(
            mother='mother',
            father='father',
        )

        self.assertEqual(
            state.name_for_role(
                'mother'
            ),
            'mother',
        )

        self.assertEqual(
            state.name_for_role(
                'father'
            ),
            'father',
        )

        with self.assertRaises(
            ValueError
        ):
            state.name_for_role(
                'guardian'
            )


if __name__ == '__main__':
    unittest.main()
