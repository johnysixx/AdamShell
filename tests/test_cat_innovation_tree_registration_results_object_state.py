import unittest

from cats.cat_group_innovation_system import (
    CatGroupInnovationSystem,
)
from cats.cat_group_innovation_tree_system import (
    CatGroupInnovationTreeSystem,
)
from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_innovation_tree_registration_state import (
    CatInnovationTreeRegisteredResult,
    CatInnovationTreeRegistrationDeniedResult,
)
from cats.cat_innovation_tree_state import (
    CatInnovationTreeState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatInnovationTreeRegistrationResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = (
            self.cats.create_cat(
                name="innovation_cat",
                color="black",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        self.group_id = (
            self.groups.create_group(
                self.cat,
                name="innovation_group",
            )[
                "group_id"
            ]
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        for knowledge_id in (
            "route",
            "danger",
            "shelter",
        ):
            self.knowledge.contribute(
                self.group_id,
                self.cat,
                knowledge_id,
                {
                    "value":
                        knowledge_id
                },
                "navigation",
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

    def create_innovation(
        self,
        name,
        knowledge_ids,
        parent=None,
    ):
        return (
            self.innovations.combine(
                self.group_id,
                knowledge_ids,
                name=name,
                category="navigation",
                procedure={
                    "rule": name
                },
                parent_innovation_id=
                    parent,
            )
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

    def test_unknown_innovation_returns_denied_object(
        self
    ):
        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        tree_count = len(
            group.innovation_tree
        )

        result = (
            self.tree.register(
                self.group_id,
                "missing_innovation",
            )
        )

        self.assertIsInstance(
            result,
            CatInnovationTreeRegistrationDeniedResult,
        )

        self.assertFalse(
            result.registered
        )

        self.assertEqual(
            result.name,
            "cat_innovation_tree_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_innovation",
        )

        self.assertEqual(
            len(
                group.innovation_tree
            ),
            tree_count,
        )

        self.assert_not_mapping(
            result
        )

    def test_root_registration_returns_object(
        self
    ):
        created = (
            self.create_innovation(
                "root",
                [
                    "route",
                    "danger",
                ],
            )
        )

        result = (
            self.tree.register(
                self.group_id,
                created.innovation_id,
            )
        )

        self.assertIsInstance(
            result,
            CatInnovationTreeRegisteredResult,
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.name,
            "cat_innovation_tree_registered",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.innovation_id,
            created.innovation_id,
        )

        self.assertIsNone(
            result.parent
        )

        self.assertEqual(
            result.generation,
            0,
        )

        self.assert_not_mapping(
            result
        )

    def test_registration_preserves_same_state_object(
        self
    ):
        created = (
            self.create_innovation(
                "root",
                [
                    "route",
                    "danger",
                ],
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        stored = (
            group.innovation_tree[
                created.innovation_id
            ]
        )

        result = (
            self.tree.register(
                self.group_id,
                created.innovation_id,
            )
        )

        current = (
            group.innovation_tree[
                result.innovation_id
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertIsInstance(
            current,
            CatInnovationTreeState,
        )

        self.assertEqual(
            current.innovation_id,
            created.innovation_id,
        )

        self.assertIsNone(
            current.parent
        )

        self.assertEqual(
            current.generation,
            0,
        )

    def test_child_registration_links_parent_and_child(
        self
    ):
        root = (
            self.create_innovation(
                "root",
                [
                    "route",
                    "danger",
                ],
            )
        )

        child = (
            self.create_innovation(
                "child",
                [
                    "route",
                    "shelter",
                ],
                parent=
                    root.innovation_id,
            )
        )

        result = (
            self.tree.register(
                self.group_id,
                child.innovation_id,
                parent_innovation_id=
                    root.innovation_id,
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        root_state = (
            group.innovation_tree[
                root.innovation_id
            ]
        )

        child_state = (
            group.innovation_tree[
                child.innovation_id
            ]
        )

        self.assertEqual(
            result.parent,
            root.innovation_id,
        )

        self.assertEqual(
            result.generation,
            1,
        )

        self.assertEqual(
            child_state.parent,
            root.innovation_id,
        )

        self.assertEqual(
            child_state.generation,
            1,
        )

        self.assertIn(
            child.innovation_id,
            root_state.children,
        )

        innovation = (
            group.innovations[
                child.innovation_id
            ]
        )

        self.assertEqual(
            innovation.parent_innovation,
            root.innovation_id,
        )

        self.assertEqual(
            innovation.generation,
            1,
        )

    def test_duplicate_child_registration_is_idempotent(
        self
    ):
        root = (
            self.create_innovation(
                "root",
                [
                    "route",
                    "danger",
                ],
            )
        )

        child = (
            self.create_innovation(
                "child",
                [
                    "route",
                    "shelter",
                ],
                parent=
                    root.innovation_id,
            )
        )

        self.tree.register(
            self.group_id,
            child.innovation_id,
            parent_innovation_id=
                root.innovation_id,
        )

        result = (
            self.tree.register(
                self.group_id,
                child.innovation_id,
                parent_innovation_id=
                    root.innovation_id,
            )
        )

        root_state = (
            self.groups.groups[
                self.group_id
            ].innovation_tree[
                root.innovation_id
            ]
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            root_state.children,
            [
                child.innovation_id
            ],
        )

    def test_missing_parent_preserves_existing_behavior(
        self
    ):
        child = (
            self.create_innovation(
                "child",
                [
                    "route",
                    "shelter",
                ],
            )
        )

        result = (
            self.tree.register(
                self.group_id,
                child.innovation_id,
                parent_innovation_id=
                    "missing_parent",
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        state = (
            group.innovation_tree[
                child.innovation_id
            ]
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.parent,
            "missing_parent",
        )

        self.assertEqual(
            result.generation,
            1,
        )

        self.assertEqual(
            state.parent,
            "missing_parent",
        )

        self.assertEqual(
            state.generation,
            1,
        )

        self.assertNotIn(
            "missing_parent",
            group.innovation_tree,
        )

    def test_descendants_and_tree_remain_collection_queries(
        self
    ):
        root = (
            self.create_innovation(
                "root",
                [
                    "route",
                    "danger",
                ],
            )
        )

        child = (
            self.create_innovation(
                "child",
                [
                    "route",
                    "shelter",
                ],
                parent=
                    root.innovation_id,
            )
        )

        descendants = (
            self.tree.descendants(
                self.group_id,
                root.innovation_id,
            )
        )

        self.assertEqual(
            descendants,
            [
                child.innovation_id
            ],
        )

        tree = (
            self.tree.tree(
                self.group_id
            )
        )

        self.assertIsInstance(
            tree[
                root.innovation_id
            ],
            CatInnovationTreeState,
        )

        self.assertIsInstance(
            tree[
                child.innovation_id
            ],
            CatInnovationTreeState,
        )

        stored = (
            self.groups.groups[
                self.group_id
            ].innovation_tree[
                root.innovation_id
            ]
        )

        self.assertIsNot(
            tree[
                root.innovation_id
            ],
            stored,
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.tree.register(
                self.group_id,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        created = (
            self.create_innovation(
                "root",
                [
                    "route",
                    "danger",
                ],
            )
        )

        registered = (
            self.tree.register(
                self.group_id,
                created.innovation_id,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            registered.generation = 99

        with self.assertRaises(
            AttributeError
        ):
            registered.innovation_id = "changed"


if __name__ == "__main__":
    unittest.main()
