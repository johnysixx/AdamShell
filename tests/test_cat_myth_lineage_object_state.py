import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem
)
from cats.cat_group_myth_system import (
    CatGroupMythSystem
)
from cats.cat_group_myth_lineage_system import (
    CatGroupMythLineageSystem
)
from cats.cat_myth_lineage_state import (
    CatMythLineageState
)


class CatMythLineageObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = self.cats.create_cat(
            name='myth_first',
            color='black',
            fur_length='short',
        )

        self.second = self.cats.create_cat(
            name='myth_second',
            color='white',
            fur_length='short',
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.first_group = (
            self.groups.create_group(
                self.first,
                name='myth_first_group',
            )[
                'group_id'
            ]
        )

        self.second_group = (
            self.groups.create_group(
                self.second,
                name='myth_second_group',
            )[
                'group_id'
            ]
        )

        knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        knowledge.contribute(
            self.first_group,
            self.first,
            'danger_scent',
            {
                'aroma': 'cronenberg'
            },
            'danger',
            confidence=1.0,
        )

        self.myths = CatGroupMythSystem(
            self.groups
        )

        self.lineages = (
            CatGroupMythLineageSystem(
                self.groups
            )
        )

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatMythLineageState(
            root_myth='root'
        )

        self.assertEqual(
            state.root_myth,
            'root',
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

    def test_created_myth_stores_object_lineage(
        self
    ):
        created = (
            self.myths
            .create_from_knowledge(
                self.first_group,
                'danger_scent',
            )
        )

        myth_id = created[
            'myth_id'
        ]

        state = (
            self.groups
            .groups[self.first_group]
            .myth_lineages[
                myth_id
            ]
        )

        self.assertIsInstance(
            state,
            CatMythLineageState,
        )

        self.assertEqual(
            state.root_myth,
            myth_id,
        )

        self.assertEqual(
            state.versions,
            [
                myth_id
            ],
        )

    def test_retelling_registers_descendant_object(
        self
    ):
        created = (
            self.myths
            .create_from_knowledge(
                self.first_group,
                'danger_scent',
            )
        )

        root = created[
            'myth_id'
        ]

        retold = self.myths.retell(
            self.first_group,
            self.second_group,
            root,
            transformation={
                'claim':
                    'all boxes are dangerous'
            },
        )

        state = self.lineages.lineage(
            self.second_group,
            root,
        )

        child = retold[
            'myth_id'
        ]

        self.assertIsInstance(
            state,
            CatMythLineageState,
        )

        self.assertIn(
            child,
            state.versions,
        )

        self.assertEqual(
            state.children[
                root
            ],
            [
                child
            ],
        )

    def test_legacy_mapping_record_is_rejected(
        self
    ):
        group = self.groups.groups[
            self.first_group
        ]

        group.myth_lineages[
            'legacy'
        ] = {
            'root_myth': 'legacy',
            'versions': [
                'legacy'
            ],
            'children': {},
        }

        with self.assertRaises(
            TypeError
        ):
            self.lineages.lineage(
                self.first_group,
                'legacy',
            )


if __name__ == '__main__':
    unittest.main()
