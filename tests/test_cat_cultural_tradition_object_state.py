import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_culture_system import (
    CatGroupCultureSystem
)
from cats.cat_group_ritual_system import (
    CatGroupRitualSystem
)
from cats.cat_cultural_tradition_state import (
    CatCulturalTraditionState
)


class CatCulturalTraditionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='tradition_cat',
            color='black',
            fur_length='short',
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.cat,
                name='tradition_group',
            )[
                'group_id'
            ]
        )

        self.culture = (
            CatGroupCultureSystem(
                self.groups
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = (
            CatCulturalTraditionState(
                name='night_patrol',
                category='exploration',
                occurrences=1,
                strength=0.2,
            )
        )

        self.assertEqual(
            state.name,
            'night_patrol',
        )

        self.assertEqual(
            state.category,
            'exploration',
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

    def test_practice_stores_and_mutates_object(
        self
    ):
        self.culture.practice(
            self.group_id,
            'night_patrol',
            'exploration',
            weight=0.2,
        )

        state = (
            self.groups
            .groups[self.group_id]
            .culture
            .traditions[
                'night_patrol'
            ]
        )

        self.assertIsInstance(
            state,
            CatCulturalTraditionState,
        )

        self.culture.practice(
            self.group_id,
            'night_patrol',
            'exploration',
            weight=0.3,
        )

        current = (
            self.groups
            .groups[self.group_id]
            .culture
            .traditions[
                'night_patrol'
            ]
        )

        self.assertIs(
            current,
            state,
        )

        self.assertEqual(
            state.occurrences,
            2,
        )

        self.assertAlmostEqual(
            state.strength,
            0.5,
        )

    def test_ritual_uses_same_tradition_object_type(
        self
    ):
        rituals = CatGroupRitualSystem(
            self.groups
        )

        rituals.define(
            self.group_id,
            'box_vigil',
            'ritual',
        )

        rituals.perform(
            self.group_id,
            'box_vigil',
            [
                self.cat
            ],
        )

        state = (
            self.groups
            .groups[self.group_id]
            .culture
            .traditions[
                'box_vigil'
            ]
        )

        self.assertIsInstance(
            state,
            CatCulturalTraditionState,
        )

        self.assertEqual(
            state.occurrences,
            1,
        )

        self.assertEqual(
            state.category,
            'ritual',
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        group = self.groups.groups[
            self.group_id
        ]

        group.culture.traditions[
            'night_patrol'
        ] = {
            'name': 'night_patrol',
            'category': 'exploration',
            'occurrences': 1,
            'strength': 0.2,
        }

        with self.assertRaises(
            TypeError
        ):
            self.culture.practice(
                self.group_id,
                'night_patrol',
                'exploration',
            )


if __name__ == '__main__':
    unittest.main()
