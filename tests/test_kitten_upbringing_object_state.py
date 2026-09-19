import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.kitten_upbringing_resolver import (
    KittenUpbringingResolver
)
from cats.kitten_upbringing_state import (
    KittenCareState,
    KittenCronenbergExperienceState,
    KittenUpbringingState,
)


class KittenUpbringingObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        self.resolver = (
            KittenUpbringingResolver(
                self.universe
            )
        )

        self.mother = self.cats.create_cat(
            name='mother',
            color='black',
            fur_length='short',
            origin='natural_birth',
        )

        self.kitten = self.cats.create_cat(
            name='kitten',
            color='white',
            fur_length='short',
            origin='kitten_birth_resolver',
        )

        self.kitten.parents = {
            'mother': 'mother',
            'father': None,
        }

        self.kitten.mother_name = 'mother'

        self.development.initialize_newborn(
            self.kitten,
            birth_day=0,
        )

    def test_state_and_nested_states_have_no_mapping_api(
        self
    ):
        state = KittenUpbringingState()

        self.assertIsInstance(
            state.care,
            KittenCareState,
        )

        self.assertIsInstance(
            state.cronenberg_experience,
            KittenCronenbergExperienceState,
        )

        for item in (
            state,
            state.care,
            state.cronenberg_experience,
        ):
            self.assertFalse(
                hasattr(
                    item,
                    'get',
                )
            )

            self.assertFalse(
                hasattr(
                    item,
                    '__getitem__',
                )
            )

            self.assertFalse(
                hasattr(
                    item,
                    '__setitem__',
                )
            )

    def test_tick_creates_object_state(
        self
    ):
        self.kitten.age_days = 1

        self.resolver.tick_day(
            kitten=self.kitten,
            cats=self.cats.cats,
            current_day=1,
        )

        self.assertIsInstance(
            self.kitten.upbringing,
            KittenUpbringingState,
        )

        self.assertEqual(
            self.kitten.upbringing
            .days_processed,
            1,
        )

        self.assertTrue(
            self.kitten.upbringing
            .care.fed_today
        )

    def test_tick_mutates_same_state_object(
        self
    ):
        state = (
            self.resolver
            ._create_upbringing_state()
        )

        self.kitten.upbringing = state
        self.kitten.age_days = 14

        self.resolver.tick_day(
            kitten=self.kitten,
            cats=self.cats.cats,
            current_day=14,
        )

        self.assertIs(
            self.kitten.upbringing,
            state,
        )

        self.assertEqual(
            state.phase,
            'early_socialization',
        )

        self.assertTrue(
            state.care.left_alone_briefly
        )

        self.assertEqual(
            state.cronenberg_experience
            .dead_deliveries,
            1,
        )

    def test_legacy_mapping_state_is_rejected(
        self
    ):
        self.kitten.upbringing = {
            'phase':
                'complete_maternal_care',
        }

        self.kitten.age_days = 1

        with self.assertRaises(
            TypeError
        ):
            self.resolver.tick_day(
                kitten=self.kitten,
                cats=self.cats.cats,
                current_day=1,
            )

    def test_legacy_nested_mapping_is_rejected(
        self
    ):
        state = KittenUpbringingState()

        state.care = {
            'fed_today': False,
        }

        self.kitten.upbringing = state
        self.kitten.age_days = 1

        with self.assertRaises(
            TypeError
        ):
            self.resolver.tick_day(
                kitten=self.kitten,
                cats=self.cats.cats,
                current_day=1,
            )


if __name__ == '__main__':
    unittest.main()
