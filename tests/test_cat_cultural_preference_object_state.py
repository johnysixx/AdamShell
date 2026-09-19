import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import CatGroupSystem
from cats.cat_group_culture_system import (
    CatGroupCultureSystem
)
from cats.cat_cultural_adoption_system import (
    CatCulturalAdoptionSystem
)
from cats.cat_cultural_preference_state import (
    CatCulturalPreferenceState
)


class CatCulturalPreferenceObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name='preference_first',
            color='black',
            fur_length='short',
        )

        self.second = self.cats.create_cat(
            name='preference_second',
            color='white',
            fur_length='short',
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.first,
                name='preference_group',
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
            CatCulturalPreferenceState(
                value='bar_cloth',
                strength=0.4,
                expressions=1,
            )
        )

        self.assertEqual(
            state.value,
            'bar_cloth',
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

    def test_registry_stores_and_mutates_object(
        self
    ):
        self.culture.express_preference(
            self.group_id,
            'sleeping_place',
            'bar_cloth',
            strength=0.2,
        )

        state = (
            self.groups
            .groups[self.group_id]
            .culture
            .preferences[
                'sleeping_place'
            ]
        )

        self.assertIsInstance(
            state,
            CatCulturalPreferenceState,
        )

        self.culture.express_preference(
            self.group_id,
            'sleeping_place',
            'window',
            strength=0.3,
        )

        current = (
            self.groups
            .groups[self.group_id]
            .culture
            .preferences[
                'sleeping_place'
            ]
        )

        self.assertIs(
            current,
            state,
        )

        self.assertEqual(
            state.value,
            'window',
        )

        self.assertEqual(
            state.expressions,
            2,
        )

        self.assertAlmostEqual(
            state.strength,
            0.5,
        )

    def test_adoption_copies_object_record(
        self
    ):
        self.culture.express_preference(
            self.group_id,
            'sleeping_place',
            'bar_cloth',
            strength=0.4,
        )

        source = (
            self.groups
            .groups[self.group_id]
            .culture
            .preferences[
                'sleeping_place'
            ]
        )

        adoption = (
            CatCulturalAdoptionSystem(
                self.groups
            )
        )

        adoption.adopt_preference(
            self.second,
            self.group_id,
            'sleeping_place',
        )

        adopted = (
            self.second
            .culture
            .preferences[
                'sleeping_place'
            ]
        )

        self.assertIsInstance(
            adopted,
            CatCulturalPreferenceState,
        )

        self.assertIsNot(
            adopted,
            source,
        )

        self.assertEqual(
            adopted.value,
            'bar_cloth',
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        group = self.groups.groups[
            self.group_id
        ]

        group.culture.preferences[
            'sleeping_place'
        ] = {
            'value': 'bar_cloth',
            'strength': 0.4,
            'expressions': 1,
        }

        with self.assertRaises(
            TypeError
        ):
            self.culture.express_preference(
                self.group_id,
                'sleeping_place',
                'window',
            )


if __name__ == '__main__':
    unittest.main()
