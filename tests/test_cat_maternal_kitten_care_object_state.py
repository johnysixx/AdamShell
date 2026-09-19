import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_family_system import (
    CatFamilySystem
)
from cats.cat_maternal_care_system import (
    CatMaternalCareSystem
)
from cats.cat_maternal_kitten_care_state import (
    CatMaternalKittenCareState
)


class CatMaternalKittenCareObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.mother = self.cats.create_cat(
            name='care_record_mother',
            color='black',
            fur_length='short',
        )

        self.mother.sex = 'female'

        self.kitten = self.cats.create_cat(
            name='care_record_kitten',
            color='white',
            fur_length='short',
        )

        self.kitten.mother_name = (
            self.mother.name
        )

        self.kitten.father_name = None

        family = CatFamilySystem(
            self.cats
        )

        family.register_birth(
            mother=self.mother,
            kittens=[
                self.kitten
            ],
            cats=self.cats.cats,
        )

        self.care = (
            CatMaternalCareSystem(
                self.cats
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = (
            CatMaternalKittenCareState()
        )

        self.assertEqual(
            state.care_events,
            0,
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

    def test_record_mutates_same_object(
        self
    ):
        state = (
            CatMaternalKittenCareState()
        )

        returned = state.record(
            day=7,
            phase=(
                'neonatal_maternal_care'
            ),
        )

        self.assertIs(
            returned,
            state,
        )

        self.assertEqual(
            state.care_events,
            1,
        )

        self.assertEqual(
            state.last_care_day,
            7,
        )

        self.assertEqual(
            state.last_phase,
            'neonatal_maternal_care',
        )

    def test_registry_keeps_same_record(
        self
    ):
        self.care.provide_care(
            self.mother,
            self.kitten,
            age_days=5,
            current_day=1,
        )

        stored = (
            self.mother
            .maternal_care
            .kittens[self.kitten.name]
        )

        self.assertIsInstance(
            stored,
            CatMaternalKittenCareState,
        )

        self.care.provide_care(
            self.mother,
            self.kitten,
            age_days=6,
            current_day=2,
        )

        current = (
            self.mother
            .maternal_care
            .kittens[self.kitten.name]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertEqual(
            stored.care_events,
            2,
        )

        self.assertEqual(
            stored.last_care_day,
            2,
        )

        self.assertEqual(
            stored.last_phase,
            'neonatal_maternal_care',
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        self.mother.maternal_care.kittens[
            self.kitten.name
        ] = {
            'care_events': 0,
            'last_care_day': None,
            'last_phase': None,
        }

        with self.assertRaises(
            TypeError
        ):
            self.care.provide_care(
                self.mother,
                self.kitten,
                age_days=5,
                current_day=1,
            )


if __name__ == '__main__':
    unittest.main()
