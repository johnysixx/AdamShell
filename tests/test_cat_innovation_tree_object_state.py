import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_group_system import (
    CatGroupSystem
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem
)
from cats.cat_group_innovation_system import (
    CatGroupInnovationSystem
)
from cats.cat_group_innovation_tree_system import (
    CatGroupInnovationTreeSystem
)
from cats.cat_innovation_tree_state import (
    CatInnovationTreeState
)


class CatInnovationTreeObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='innovation_tree_cat',
            color='black',
            fur_length='short',
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.group_id = (
            self.groups.create_group(
                self.cat,
                name='innovation_tree_group',
            )[
                'group_id'
            ]
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        for knowledge_id in (
            'route',
            'danger',
            'shelter',
        ):
            self.knowledge.contribute(
                self.group_id,
                self.cat,
                knowledge_id,
                {
                    'value':
                        knowledge_id
                },
                'navigation',
                confidence=1.0,
            )

        self.innovations = (
            CatGroupInnovationSystem(
                self.groups
            )
        )

        self.tree = (
            CatGroupInnovationTreeSystem(
                self.groups
            )
        )

    def _create(
        self,
        name,
        knowledge_ids,
        parent=None,
    ):
        return self.innovations.combine(
            self.group_id,
            knowledge_ids,
            name=name,
            category='navigation',
            procedure={
                'rule': name
            },
            parent_innovation_id=parent,
        )[
            'innovation_id'
        ]

    def test_state_has_no_mapping_api(
        self
    ):
        state = CatInnovationTreeState(
            innovation_id='root'
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
        root = self._create(
            'root',
            [
                'route',
                'danger',
            ],
        )

        state = (
            self.groups
            .groups[self.group_id]
            .innovation_tree[root]
        )

        self.assertIsInstance(
            state,
            CatInnovationTreeState,
        )

        self.assertEqual(
            state.innovation_id,
            root,
        )

        self.assertIsNone(
            state.parent
        )

        self.assertEqual(
            state.generation,
            0,
        )

    def test_child_registration_links_objects(
        self
    ):
        root = self._create(
            'root',
            [
                'route',
                'danger',
            ],
        )

        child = self._create(
            'child',
            [
                'route',
                'shelter',
            ],
            parent=root,
        )

        group = self.groups.groups[
            self.group_id
        ]

        root_state = (
            group.innovation_tree[root]
        )

        child_state = (
            group.innovation_tree[child]
        )

        self.assertEqual(
            root_state.children,
            [
                child
            ],
        )

        self.assertEqual(
            child_state.parent,
            root,
        )

        self.assertEqual(
            child_state.generation,
            1,
        )

        self.assertEqual(
            self.tree.descendants(
                self.group_id,
                root,
            ),
            [
                child
            ],
        )

    def test_legacy_mapping_parent_is_rejected(
        self
    ):
        root = self._create(
            'root',
            [
                'route',
                'danger',
            ],
        )

        group = self.groups.groups[
            self.group_id
        ]

        group.innovation_tree[
            root
        ] = {
            'innovation_id': root,
            'parent': None,
            'children': [],
            'generation': 0,
        }

        innovation_count = len(
            group.innovation_tree
        )

        with self.assertRaises(
            TypeError
        ):
            self._create(
                'child',
                [
                    'route',
                    'shelter',
                ],
                parent=root,
            )

        self.assertEqual(
            len(
                group.innovation_tree
            ),
            innovation_count,
        )


if __name__ == '__main__':
    unittest.main()
