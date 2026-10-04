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
from cats.cat_ritual_lineage_state import (
    CatRitualLineageState,
)
from cats.cat_ritual_mutation_state import (
    CatGroupRitualMutatedEvent,
    CatRitualMutationDeniedResult,
)
from cats.cats import Cats
from universe.universe import Universe


class CatRitualMutationObjectStateTests(
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

    def define_parent(
        self,
        name="night_watch",
    ):
        self.rituals.define(
            self.group_id,
            name,
            "territory",
            required_roles=[
                "guardian"
            ],
        )

        return (
            self.groups.groups[
                self.group_id
            ].rituals[
                name
            ]
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

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "mutated"
            ]

    def test_unknown_parent_returns_denied_object(
        self
    ):
        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        history_before = len(
            group.history
        )

        result = (
            self.evolution.mutate(
                self.group_id,
                "missing_ritual",
                "child_ritual",
            )
        )

        self.assertIsInstance(
            result,
            CatRitualMutationDeniedResult,
        )

        self.assertFalse(
            result.mutated
        )

        self.assertEqual(
            result.name,
            "cat_ritual_mutation_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_parent_ritual",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assertNotIn(
            "child_ritual",
            group.rituals,
        )

        self.assertEqual(
            len(group.history),
            history_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_existing_name_returns_denied_without_mutation(
        self
    ):
        parent = self.define_parent(
            "night_watch"
        )

        existing = self.define_parent(
            "existing_watch"
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        history_before = len(
            group.history
        )

        result = (
            self.evolution.mutate(
                self.group_id,
                "night_watch",
                "existing_watch",
            )
        )

        self.assertIsInstance(
            result,
            CatRitualMutationDeniedResult,
        )

        self.assertEqual(
            result.reason,
            "ritual_name_exists",
        )

        self.assertIs(
            group.rituals[
                "night_watch"
            ],
            parent,
        )

        self.assertIs(
            group.rituals[
                "existing_watch"
            ],
            existing,
        )

        self.assertEqual(
            len(group.history),
            history_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_mutation_returns_event_object(
        self
    ):
        self.define_parent()

        result = (
            self.evolution.mutate(
                self.group_id,
                "night_watch",
                "silent_watch",
                mutation_reason=
                    "quiet_patrol",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupRitualMutatedEvent,
        )

        self.assertTrue(
            result.mutated
        )

        self.assertEqual(
            result.name,
            "cat_group_ritual_mutated",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.parent_ritual,
            "night_watch",
        )

        self.assertEqual(
            result.new_ritual,
            "silent_watch",
        )

        self.assertEqual(
            result.lineage_root,
            "night_watch",
        )

        self.assertEqual(
            result.generation,
            1,
        )

        self.assertEqual(
            result.reason,
            "quiet_patrol",
        )

        self.assert_not_mapping(
            result
        )

    def test_mutation_creates_distinct_child_object(
        self
    ):
        parent = self.define_parent()

        parent.strength = 0.8
        parent.performances = 4

        result = (
            self.evolution.mutate(
                self.group_id,
                "night_watch",
                "silent_watch",
                category="stealth",
                required_roles=[
                    "night_guardian"
                ],
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        child = (
            group.rituals[
                result.new_ritual
            ]
        )

        self.assertIsNot(
            child,
            parent,
        )

        self.assertEqual(
            child.name,
            "silent_watch",
        )

        self.assertEqual(
            child.category,
            "stealth",
        )

        self.assertEqual(
            child.required_roles,
            [
                "night_guardian"
            ],
        )

        self.assertEqual(
            child.performances,
            0,
        )

        self.assertAlmostEqual(
            child.strength,
            0.56,
        )

        self.assertEqual(
            child.lineage_root,
            "night_watch",
        )

        self.assertEqual(
            child.parent_ritual,
            "night_watch",
        )

        self.assertEqual(
            child.generation,
            1,
        )

        self.assertEqual(
            child.mutation_reason,
            "local_adaptation",
        )

        self.assertEqual(
            parent.performances,
            4,
        )

        self.assertAlmostEqual(
            parent.strength,
            0.8,
        )

    def test_mutation_preserves_same_lineage_object(
        self
    ):
        self.define_parent()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        lineage = (
            group.ritual_lineages[
                "night_watch"
            ]
        )

        result = (
            self.evolution.mutate(
                self.group_id,
                "night_watch",
                "silent_watch",
            )
        )

        current = (
            group.ritual_lineages[
                result.lineage_root
            ]
        )

        self.assertIs(
            current,
            lineage,
        )

        self.assertIsInstance(
            current,
            CatRitualLineageState,
        )

        self.assertEqual(
            current.versions,
            [
                "night_watch",
                "silent_watch",
            ],
        )

        self.assertEqual(
            current.children[
                "night_watch"
            ],
            [
                "silent_watch"
            ],
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        self.define_parent()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        result = (
            self.evolution.mutate(
                self.group_id,
                "night_watch",
                "silent_watch",
                mutation_reason=
                    "quiet_patrol",
            )
        )

        stored = (
            group.history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            dict,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assertEqual(
            stored,
            result.to_dict(),
        )

        self.assertEqual(
            stored[
                "new_ritual"
            ],
            "silent_watch",
        )

    def test_history_snapshot_is_detached(
        self
    ):
        self.define_parent()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        result = (
            self.evolution.mutate(
                self.group_id,
                "night_watch",
                "silent_watch",
            )
        )

        stored = (
            group.history[
                -1
            ]
        )

        stored[
            "new_ritual"
        ] = "changed"

        self.assertEqual(
            result.new_ritual,
            "silent_watch",
        )

        fresh = (
            result.to_dict()
        )

        fresh[
            "reason"
        ] = "changed"

        self.assertEqual(
            result.reason,
            "local_adaptation",
        )

        self.assertEqual(
            stored[
                "reason"
            ],
            "local_adaptation",
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.evolution.mutate(
                self.group_id,
                "missing",
                "child",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        self.define_parent()

        result = (
            self.evolution.mutate(
                self.group_id,
                "night_watch",
                "silent_watch",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            result.new_ritual = "changed"

        with self.assertRaises(
            AttributeError
        ):
            result.generation = 99


if __name__ == "__main__":
    unittest.main()
