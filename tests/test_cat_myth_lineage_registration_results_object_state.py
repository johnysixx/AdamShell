import unittest

from cats.cat_group_knowledge_system import (
    CatGroupKnowledgeSystem,
)
from cats.cat_group_myth_lineage_system import (
    CatGroupMythLineageSystem,
)
from cats.cat_group_myth_system import (
    CatGroupMythSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_myth_lineage_registration_state import (
    CatMythDescendantRegisteredResult,
    CatMythLineageRegisteredResult,
    CatMythLineageRegistrationDeniedResult,
)
from cats.cat_myth_lineage_state import (
    CatMythLineageState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatMythLineageRegistrationResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.first = (
            self.cats.create_cat(
                name="first",
                color="black",
                fur_length="short",
            )
        )

        self.second = (
            self.cats.create_cat(
                name="second",
                color="white",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        self.first_group = (
            self.groups.create_group(
                self.first,
                name="first_group",
            )[
                "group_id"
            ]
        )

        self.second_group = (
            self.groups.create_group(
                self.second,
                name="second_group",
            )[
                "group_id"
            ]
        )

        self.knowledge = (
            CatGroupKnowledgeSystem(
                self.groups
            )
        )

        self.myths = (
            CatGroupMythSystem(
                self.groups
            )
        )

        self.lineages = (
            CatGroupMythLineageSystem(
                self.groups
            )
        )

    def contribute_source(
        self
    ):
        self.knowledge.contribute(
            self.first_group,
            self.first,
            "danger_scent",
            {
                "aroma": "cronenberg",
            },
            "danger",
            confidence=1.0,
        )

    def create_myth(
        self
    ):
        self.contribute_source()

        return (
            self.myths.create_from_knowledge(
                self.first_group,
                "danger_scent",
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

    def test_unknown_myth_returns_denied_object(
        self
    ):
        group = (
            self.groups.groups[
                self.first_group
            ]
        )

        lineage_count = len(
            group.myth_lineages
        )

        result = (
            self.lineages.register_origin(
                self.first_group,
                "missing_myth",
            )
        )

        self.assertIsInstance(
            result,
            CatMythLineageRegistrationDeniedResult,
        )

        self.assertFalse(
            result.registered
        )

        self.assertEqual(
            result.name,
            "cat_myth_lineage_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_myth",
        )

        self.assertEqual(
            len(
                group.myth_lineages
            ),
            lineage_count,
        )

        self.assert_not_mapping(
            result
        )

    def test_register_origin_returns_object(
        self
    ):
        created = (
            self.create_myth()
        )

        result = (
            self.lineages.register_origin(
                self.first_group,
                created.myth_id,
            )
        )

        self.assertIsInstance(
            result,
            CatMythLineageRegisteredResult,
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.name,
            "cat_myth_lineage_registered",
        )

        self.assertEqual(
            result.group_id,
            self.first_group,
        )

        self.assertEqual(
            result.myth_id,
            created.myth_id,
        )

        self.assert_not_mapping(
            result
        )

    def test_register_origin_preserves_same_lineage_object(
        self
    ):
        created = (
            self.create_myth()
        )

        group = (
            self.groups.groups[
                self.first_group
            ]
        )

        stored = (
            group.myth_lineages[
                created.myth_id
            ]
        )

        result = (
            self.lineages.register_origin(
                self.first_group,
                created.myth_id,
            )
        )

        current = (
            group.myth_lineages[
                result.myth_id
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertIsInstance(
            current,
            CatMythLineageState,
        )

        self.assertEqual(
            current.versions,
            [
                created.myth_id
            ],
        )

    def test_register_origin_resets_origin_state(
        self
    ):
        created = (
            self.create_myth()
        )

        group = (
            self.groups.groups[
                self.first_group
            ]
        )

        myth = (
            group.myths[
                created.myth_id
            ]
        )

        myth.lineage_root = "changed"
        myth.parent_version = "parent"
        myth.generation = 5

        result = (
            self.lineages.register_origin(
                self.first_group,
                created.myth_id,
            )
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            myth.lineage_root,
            created.myth_id,
        )

        self.assertIsNone(
            myth.parent_version
        )

        self.assertEqual(
            myth.generation,
            0,
        )

    def test_register_descendant_returns_object(
        self
    ):
        result = (
            self.lineages.register_descendant(
                self.second_group,
                "root_myth",
                "parent_myth",
                "child_myth",
            )
        )

        self.assertIsInstance(
            result,
            CatMythDescendantRegisteredResult,
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.name,
            "cat_myth_descendant_registered",
        )

        self.assertEqual(
            result.group_id,
            self.second_group,
        )

        self.assertEqual(
            result.root_myth_id,
            "root_myth",
        )

        self.assertEqual(
            result.parent_myth_id,
            "parent_myth",
        )

        self.assertEqual(
            result.child_myth_id,
            "child_myth",
        )

        self.assert_not_mapping(
            result
        )

    def test_register_descendant_creates_object_lineage(
        self
    ):
        result = (
            self.lineages.register_descendant(
                self.second_group,
                "root_myth",
                "parent_myth",
                "child_myth",
            )
        )

        group = (
            self.groups.groups[
                self.second_group
            ]
        )

        lineage = (
            group.myth_lineages[
                result.root_myth_id
            ]
        )

        self.assertIsInstance(
            lineage,
            CatMythLineageState,
        )

        self.assertEqual(
            lineage.root_myth,
            "root_myth",
        )

        self.assertEqual(
            lineage.versions,
            [
                "root_myth",
                "child_myth",
            ],
        )

        self.assertEqual(
            lineage.children[
                "parent_myth"
            ],
            [
                "child_myth"
            ],
        )

    def test_repeated_descendant_registration_reuses_lineage(
        self
    ):
        first = (
            self.lineages.register_descendant(
                self.second_group,
                "root_myth",
                "parent_myth",
                "child_myth",
            )
        )

        group = (
            self.groups.groups[
                self.second_group
            ]
        )

        stored = (
            group.myth_lineages[
                first.root_myth_id
            ]
        )

        second = (
            self.lineages.register_descendant(
                self.second_group,
                "root_myth",
                "parent_myth",
                "second_child",
            )
        )

        current = (
            group.myth_lineages[
                second.root_myth_id
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertEqual(
            current.versions,
            [
                "root_myth",
                "child_myth",
                "second_child",
            ],
        )

        self.assertEqual(
            current.children[
                "parent_myth"
            ],
            [
                "child_myth",
                "second_child",
            ],
        )

    def test_duplicate_descendant_registration_is_idempotent(
        self
    ):
        self.lineages.register_descendant(
            self.second_group,
            "root_myth",
            "parent_myth",
            "child_myth",
        )

        result = (
            self.lineages.register_descendant(
                self.second_group,
                "root_myth",
                "parent_myth",
                "child_myth",
            )
        )

        lineage = (
            self.groups.groups[
                self.second_group
            ].myth_lineages[
                result.root_myth_id
            ]
        )

        self.assertEqual(
            lineage.versions,
            [
                "root_myth",
                "child_myth",
            ],
        )

        self.assertEqual(
            lineage.children[
                "parent_myth"
            ],
            [
                "child_myth"
            ],
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.lineages.register_origin(
                self.first_group,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        created = (
            self.create_myth()
        )

        registered = (
            self.lineages.register_origin(
                self.first_group,
                created.myth_id,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            registered.myth_id = "changed"

        descendant = (
            self.lineages.register_descendant(
                self.second_group,
                "root",
                "parent",
                "child",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            descendant.child_myth_id = "changed"


if __name__ == "__main__":
    unittest.main()
