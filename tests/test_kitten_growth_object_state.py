import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.kitten_growth import KittenGrowth
from cats.kitten_growth_state import (
    KittenGrowthState,
)


class KittenGrowthObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.growth = KittenGrowth(
            self.universe
        )

        self.kitten = self.cats.create_cat(
            name='growth_object_kitten',
            color='white',
            fur_length='short',
            origin='test',
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = KittenGrowthState()

        self.assertEqual(
            state.milk_feedings,
            0,
        )

        self.assertEqual(
            state.processed_sources,
            [],
        )

        self.assertEqual(
            state.history,
            [],
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

    def test_ensure_state_creates_object(
        self
    ):
        state = self.growth.ensure_state(
            self.kitten
        )

        self.assertIsInstance(
            state,
            KittenGrowthState,
        )

        self.assertIs(
            self.kitten.growth,
            state,
        )

    def test_growth_mutates_same_object(
        self
    ):
        state = self.growth.ensure_state(
            self.kitten
        )

        self.growth.feed_cat_milk(
            self.kitten,
            day=1,
            amount=1.0,
        )

        self.assertIs(
            self.kitten.growth,
            state,
        )

        self.assertEqual(
            state.milk_feedings,
            1,
        )

        self.assertGreater(
            state.size_gained,
            0.0,
        )

        self.assertEqual(
            len(state.history),
            1,
        )

    def test_legacy_mapping_state_is_rejected(
        self
    ):
        self.kitten.growth = {
            'milk_feedings': 0,
        }

        with self.assertRaises(
            TypeError
        ):
            self.growth.ensure_state(
                self.kitten
            )


if __name__ == '__main__':
    unittest.main()
