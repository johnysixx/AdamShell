import unittest

from cats.cat_group_ritual_evolution_system import (
    CatGroupRitualEvolutionSystem,
)
from cats.cat_group_ritual_system import (
    CatGroupRitualSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cat_ritual_lineage_registration_state import (
    CatRitualLineageRegisteredResult,
    CatRitualLineageRegistrationDeniedResult,
)
from cats.cat_ritual_lineage_state import (
    CatRitualLineageState,
)
from cats.cats import Cats
from universe.universe import Universe


class CatRitualLineageRegistrationObjectStateTests(
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
            created_group[
                "group_id"
            ]
        )

        self.rituals = (
            CatGroupRitualSystem(
                self.groups
            )
        )

        self.evolution = (
            CatGroupRitualEvolutionSystem(
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
                "registered"
            ]

    def test_unknown_ritual_returns_denied_object(
        self
    ):
        result = (
            self.evolution.register_origin(
                self.group_id,
                "missing_ritual",
            )
        )

        self.assertIsInstance(
            result,
            CatRitualLineageRegistrationDeniedResult,
        )

        self.assertFalse(
            result.registered
        )

        self.assertEqual(
            result.name,
            "cat_ritual_lineage_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_ritual",
        )

        self.assert_not_mapping(
            result
        )

    def test_existing_ritual_returns_registered_object(
        self
    ):
        self.rituals.define(
            self.group_id,
            "night_watch",
            "territory",
        )

        result = (
            self.evolution.register_origin(
                self.group_id,
                "night_watch",
            )
        )

        self.assertIsInstance(
            result,
            CatRitualLineageRegisteredResult,
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            result.name,
            "cat_ritual_lineage_registered",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.ritual,
            "night_watch",
        )

        self.assert_not_mapping(
            result
        )

    def test_registration_preserves_lineage_object(
        self
    ):
        self.rituals.define(
            self.group_id,
            "night_watch",
            "territory",
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        stored = (
            group.ritual_lineages[
                "night_watch"
            ]
        )

        result = (
            self.evolution.register_origin(
                self.group_id,
                "night_watch",
            )
        )

        current = (
            group.ritual_lineages[
                result.ritual
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertIsInstance(
            current,
            CatRitualLineageState,
        )

        self.assertEqual(
            current.root_ritual,
            "night_watch",
        )

        self.assertEqual(
            current.versions,
            [
                "night_watch"
            ],
        )

    def test_registration_sets_ritual_origin_state(
        self
    ):
        self.rituals.define(
            self.group_id,
            "evening_patrol",
            "territory",
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        ritual = (
            group.rituals[
                "evening_patrol"
            ]
        )

        ritual.lineage_root = "changed"
        ritual.parent_ritual = "parent"
        ritual.generation = 4

        result = (
            self.evolution.register_origin(
                self.group_id,
                "evening_patrol",
            )
        )

        self.assertTrue(
            result.registered
        )

        self.assertEqual(
            ritual.lineage_root,
            "evening_patrol",
        )

        self.assertIsNone(
            ritual.parent_ritual
        )

        self.assertEqual(
            ritual.generation,
            0,
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.evolution.register_origin(
                self.group_id,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        self.rituals.define(
            self.group_id,
            "night_watch",
            "territory",
        )

        registered = (
            self.evolution.register_origin(
                self.group_id,
                "night_watch",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            registered.ritual = "changed"


if __name__ == "__main__":
    unittest.main()
