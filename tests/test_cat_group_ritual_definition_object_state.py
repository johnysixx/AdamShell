import unittest

from cats.cat_group_ritual_definition_state import (
    CatGroupRitualDefinedResult,
)
from cats.cat_group_ritual_system import (
    CatGroupRitualSystem,
)
from cats.cat_group_ritual_registry import (
    CatGroupRitualLineageRegistry,
    CatGroupRitualRegistry,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_ritual_lineage_state import (
    CatRitualLineageState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupRitualDefinitionObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.founder = (
            self.cats.create_cat(
                name="founder",
                color="black",
                fur_length="short",
            )
        )

        self.groups = (
            CatGroupSystem(
                self.cats
            )
        )

        created_group = (
            self.groups.create_group(
                self.founder,
                name="bar_cats",
            )
        )

        self.group_id = (
            created_group.group_id
        )

        self.rituals = (
            CatGroupRitualSystem(
                self.groups
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
                "ritual"
            ]

    def test_group_ritual_registries_have_no_mapping_api(
        self
    ):
        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        self.assertIsInstance(
            group.rituals,
            CatGroupRitualRegistry,
        )

        self.assertIsInstance(
            group.ritual_lineages,
            CatGroupRitualLineageRegistry,
        )

        for registry in (
            group.rituals,
            group.ritual_lineages,
        ):
            self.assertTrue(
                registry.is_empty
            )

            self.assertEqual(
                registry.count,
                0,
            )

            self.assertEqual(
                registry.records(),
                (),
            )

            for mapping_method in (
                "get",
                "keys",
                "items",
                "values",
                "pop",
                "setdefault",
                "clear",
                "__getitem__",
                "__setitem__",
                "__contains__",
                "__iter__",
            ):
                self.assertFalse(
                    hasattr(
                        registry,
                        mapping_method,
                    )
                )

        with self.assertRaises(
            TypeError
        ):
            group.rituals.store(
                {
                    "name": "legacy",
                }
            )

        with self.assertRaises(
            TypeError
        ):
            group.ritual_lineages.store(
                {
                    "root_ritual": "legacy",
                }
            )

    def test_define_returns_object_result(
        self
    ):
        result = (
            self.rituals.define(
                self.group_id,
                "evening_patrol",
                "territory",
                required_roles=[
                    "guardian"
                ],
            )
        )

        self.assertIsInstance(
            result,
            CatGroupRitualDefinedResult,
        )

        self.assertTrue(
            result.defined
        )

        self.assertEqual(
            result.name,
            "cat_group_ritual_defined",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.ritual,
            "evening_patrol",
        )

        self.assert_not_mapping(
            result
        )

    def test_definition_creates_ritual_object(
        self
    ):
        result = (
            self.rituals.define(
                self.group_id,
                "evening_patrol",
                "territory",
                required_roles=[
                    "guardian"
                ],
            )
        )

        ritual = (
            self.groups.groups[
                self.group_id
            ].rituals.record(result.ritual)
        )

        self.assertEqual(
            ritual.name,
            "evening_patrol",
        )

        self.assertEqual(
            ritual.category,
            "territory",
        )

        self.assertEqual(
            ritual.required_roles,
            [
                "guardian"
            ],
        )

        self.assertEqual(
            ritual.performances,
            0,
        )

        self.assertEqual(
            ritual.strength,
            0.0,
        )

    def test_definition_preserves_lineage_origin(
        self
    ):
        result = (
            self.rituals.define(
                self.group_id,
                "night_watch",
                "territory",
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        ritual = (
            group.rituals.record(result.ritual)
        )

        lineage = (
            group.ritual_lineages.record(result.ritual)
        )

        self.assertEqual(
            ritual.lineage_root,
            result.ritual,
        )

        self.assertIsNone(
            ritual.parent_ritual
        )

        self.assertEqual(
            ritual.generation,
            0,
        )

        self.assertIsInstance(
            lineage,
            CatRitualLineageState,
        )

        self.assertEqual(
            lineage.root_ritual,
            result.ritual,
        )

        self.assertEqual(
            lineage.versions,
            [
                result.ritual
            ],
        )

    def test_definition_result_is_immutable(
        self
    ):
        result = (
            self.rituals.define(
                self.group_id,
                "box_vigil",
                "ritual",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            result.ritual = (
                "changed"
            )


if __name__ == "__main__":
    unittest.main()
