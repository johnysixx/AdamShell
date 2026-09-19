import unittest

from cats.cat_group_memory_state import (
    CatGroupMemoryState,
)
from cats.cat_group_memory_system import (
    CatGroupMemorySystem,
)
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupMemoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        first_cat = (
            self.cats.create_cat(
                name='memory_first_cat',
                color='black',
                fur_length='short',
            )
        )

        second_cat = (
            self.cats.create_cat(
                name='memory_second_cat',
                color='white',
                fur_length='short',
            )
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                first_cat,
                name='memory_first_group',
            )['group_id']
        )

        self.second_group = (
            self.groups.create_group(
                second_cat,
                name='memory_second_group',
            )['group_id']
        )

        self.memory = (
            CatGroupMemorySystem(
                self.groups
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatGroupMemoryState()

        self.assertEqual(
            state.encounters,
            0,
        )

        self.assertEqual(
            state.recent_events,
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

    def test_registry_stores_object_record(
        self
    ):
        self.memory.record_cooperation(
            self.first_group,
            self.second_group,
            cooperation_type='shared_hunt',
        )

        group = self.groups.groups[
            self.first_group
        ]

        state = group.group_memory[
            self.second_group
        ]

        self.assertIsInstance(
            state,
            CatGroupMemoryState,
        )

        self.assertEqual(
            state.encounters,
            1,
        )

        self.assertEqual(
            state.cooperations,
            1,
        )

    def test_relation_memory_returns_object_snapshot(
        self
    ):
        self.memory.record_cooperation(
            self.first_group,
            self.second_group,
            cooperation_type='shared_hunt',
        )

        stored = (
            self.groups
            .groups[self.first_group]
            .group_memory[self.second_group]
        )

        snapshot = (
            self.memory.relation_memory(
                self.first_group,
                self.second_group,
            )
        )

        self.assertIsInstance(
            snapshot,
            CatGroupMemoryState,
        )

        self.assertIsNot(
            snapshot,
            stored,
        )

        snapshot.cooperations = 99

        self.assertEqual(
            stored.cooperations,
            1,
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        group = self.groups.groups[
            self.first_group
        ]

        group.group_memory[
            self.second_group
        ] = {
            'encounters': 0,
        }

        with self.assertRaises(
            TypeError
        ):
            self.memory.relation_memory(
                self.first_group,
                self.second_group,
            )


if __name__ == '__main__':
    unittest.main()
