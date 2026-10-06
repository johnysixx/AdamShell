import unittest

from core.entity.components import (
    SpatialVector3,
)
from cats.cat_group_cultural_inheritance_state import (
    CatGroupCultureDivergenceResult,
    CatGroupCultureInheritedEvent,
)
from cats.cat_group_cultural_inheritance_system import (
    CatGroupCulturalInheritanceSystem,
)
from cats.cat_group_migration_state import (
    CatGroupMigratedEvent,
    CatGroupMigrationDeniedResult,
)
from cats.cat_group_migration_system import (
    CatGroupMigrationSystem,
)
from cats.cat_group_split_state import (
    CatGroupSplitDeniedResult,
    CatGroupSplitEvent,
)
from cats.cat_group_split_system import (
    CatGroupSplitSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupStructuralTransitionsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.members = [
            self.cats.create_cat(
                name=f"member_{index}",
                color="black",
                fur_length="short",
            )
            for index in range(4)
        ]

        self.outsider = (
            self.cats.create_cat(
                name="outsider",
                color="white",
                fur_length="short",
            )
        )

        self.groups = CatGroupSystem(
            self.cats
        )

        self.parent_group = (
            self.groups.create_group(
                self.members[0],
                name="parent",
            ).group_id
        )

        for cat in self.members[1:]:
            joined = (
                self.groups.add_member(
                    self.parent_group,
                    cat,
                    self.cats.cats,
                )
            )

            self.assertTrue(
                joined.joined
            )

    def assert_not_mapping(
        self,
        value,
        key,
    ):
        for method_name in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    method_name,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                key
            ]

    def _split(self):
        return (
            CatGroupSplitSystem(
                self.groups
            ).split(
                self.parent_group,
                self.cats.cats,
                departing_members=[
                    self.members[2].name,
                    self.members[3].name,
                ],
                new_name="daughter",
            )
        )

    def _child_group(self):
        return (
            self.groups.create_group(
                self.outsider,
                name="child",
            ).group_id
        )

    def test_split_returns_object_event(
        self
    ):
        result = self._split()

        self.assertIsInstance(
            result,
            CatGroupSplitEvent,
        )

        self.assertTrue(
            result.split
        )

        self.assertEqual(
            result.parent_group,
            self.parent_group,
        )

        self.assertEqual(
            result.departing_members,
            (
                self.members[2].name,
                self.members[3].name,
            ),
        )

        self.assertIsInstance(
            result.remaining_members,
            tuple,
        )

        self.assert_not_mapping(
            result,
            "daughter_group",
        )

    def test_split_history_uses_detached_object_events(
        self
    ):
        result = self._split()

        parent_event = (
            self.groups.groups[
                self.parent_group
            ].history[
                -1
            ]
        )

        daughter_event = (
            self.groups.groups[
                result.daughter_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            parent_event,
            CatGroupSplitEvent,
        )

        self.assertIsInstance(
            daughter_event,
            CatGroupSplitEvent,
        )

        self.assertEqual(
            parent_event,
            result,
        )

        self.assertEqual(
            daughter_event,
            result,
        )

        self.assertIsNot(
            parent_event,
            result,
        )

        self.assertIsNot(
            daughter_event,
            result,
        )

        self.assertIsNot(
            parent_event,
            daughter_event,
        )

    def test_split_denial_is_object(
        self
    ):
        parent = self.groups.groups[
            self.parent_group
        ]

        parent.dissolved = True

        result = (
            CatGroupSplitSystem(
                self.groups
            ).split(
                self.parent_group,
                self.cats.cats,
                departing_members=[
                    self.members[2].name,
                ],
            )
        )

        self.assertIsInstance(
            result,
            CatGroupSplitDeniedResult,
        )

        self.assertFalse(
            result.split
        )

        self.assertEqual(
            result.reason,
            "group_dissolved",
        )

        self.assert_not_mapping(
            result,
            "split",
        )

    def test_split_inherits_parent_culture(
        self
    ):
        parent = self.groups.groups[
            self.parent_group
        ]

        parent.culture.traits[
            "night_patrol"
        ] = 1.0

        result = self._split()

        daughter = self.groups.groups[
            result.daughter_group
        ]

        self.assertEqual(
            daughter.cultural_parent_group,
            self.parent_group,
        )

        self.assertAlmostEqual(
            daughter.culture.traits[
                "night_patrol"
            ],
            0.7,
        )

    def test_migration_returns_object_with_spatial_position(
        self
    ):
        migration = (
            CatGroupMigrationSystem(
                self.groups
            )
        )

        position = SpatialVector3(
            x=2.0,
            y=1.0,
            z=0.5,
        )

        result = migration.migrate(
            self.parent_group,
            self.cats.cats,
            layer="meeting_place",
            location="back_room",
            position=position,
        )

        self.assertIsInstance(
            result,
            CatGroupMigratedEvent,
        )

        self.assertTrue(
            result.migrated
        )

        self.assertIs(
            result.position,
            position,
        )

        self.assertEqual(
            result.members,
            tuple(
                cat.name
                for cat in self.members
            ),
        )

        self.assert_not_mapping(
            result,
            "position",
        )

    def test_migration_history_uses_object_events(
        self
    ):
        migration = (
            CatGroupMigrationSystem(
                self.groups
            )
        )

        result = migration.migrate(
            self.parent_group,
            self.cats.cats,
            layer="meeting_place",
            location="back_room",
        )

        stored = (
            self.groups.groups[
                self.parent_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            stored,
            CatGroupMigratedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        for cat in self.members:
            event = (
                cat.social_interactions[
                    -1
                ]
            )

            self.assertIsInstance(
                event,
                CatGroupMigratedEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

    def test_migration_denials_are_objects(
        self
    ):
        migration = (
            CatGroupMigrationSystem(
                self.groups
            )
        )

        parent = self.groups.groups[
            self.parent_group
        ]

        parent.dissolved = True

        dissolved = migration.migrate(
            self.parent_group,
            self.cats.cats,
            layer="meeting_place",
            location="back_room",
        )

        self.assertIsInstance(
            dissolved,
            CatGroupMigrationDeniedResult,
        )

        self.assertEqual(
            dissolved.reason,
            "group_dissolved",
        )

        parent.dissolved = False
        parent.members = []

        empty = migration.migrate(
            self.parent_group,
            self.cats.cats,
            layer="meeting_place",
            location="back_room",
        )

        self.assertIsInstance(
            empty,
            CatGroupMigrationDeniedResult,
        )

        self.assertEqual(
            empty.reason,
            "no_members",
        )

        self.assertFalse(
            empty.migrated
        )

    def test_cultural_inheritance_returns_object_event(
        self
    ):
        child_group = (
            self._child_group()
        )

        parent = self.groups.groups[
            self.parent_group
        ]

        parent.culture.traits[
            "window_watch"
        ] = 1.0

        inheritance = (
            CatGroupCulturalInheritanceSystem(
                self.groups
            )
        )

        result = inheritance.inherit(
            self.parent_group,
            child_group,
            retention=0.6,
        )

        self.assertIsInstance(
            result,
            CatGroupCultureInheritedEvent,
        )

        self.assertEqual(
            result.inherited_traits,
            (
                "window_watch",
            ),
        )

        self.assertAlmostEqual(
            result.retention,
            0.6,
        )

        self.assert_not_mapping(
            result,
            "retention",
        )

    def test_cultural_inheritance_history_is_object_state(
        self
    ):
        child_group = (
            self._child_group()
        )

        inheritance = (
            CatGroupCulturalInheritanceSystem(
                self.groups
            )
        )

        result = inheritance.inherit(
            self.parent_group,
            child_group,
        )

        parent_event = (
            self.groups.groups[
                self.parent_group
            ].history[
                -1
            ]
        )

        child_event = (
            self.groups.groups[
                child_group
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            parent_event,
            CatGroupCultureInheritedEvent,
        )

        self.assertIsInstance(
            child_event,
            CatGroupCultureInheritedEvent,
        )

        self.assertEqual(
            parent_event,
            result,
        )

        self.assertEqual(
            child_event,
            result,
        )

        self.assertIsNot(
            parent_event,
            child_event,
        )

    def test_divergence_returns_object_result(
        self
    ):
        child_group = (
            self._child_group()
        )

        parent = self.groups.groups[
            self.parent_group
        ]

        child = self.groups.groups[
            child_group
        ]

        parent.culture.traits[
            "exploration"
        ] = 1.0

        child.culture.traits[
            "exploration"
        ] = 0.2

        inheritance = (
            CatGroupCulturalInheritanceSystem(
                self.groups
            )
        )

        result = inheritance.divergence(
            self.parent_group,
            child_group,
        )

        self.assertIsInstance(
            result,
            CatGroupCultureDivergenceResult,
        )

        self.assertGreater(
            result.divergence,
            0.0,
        )

        self.assert_not_mapping(
            result,
            "divergence",
        )

    def test_empty_culture_divergence_is_zero_object(
        self
    ):
        child_group = (
            self._child_group()
        )

        inheritance = (
            CatGroupCulturalInheritanceSystem(
                self.groups
            )
        )

        result = inheritance.divergence(
            self.parent_group,
            child_group,
        )

        self.assertIsInstance(
            result,
            CatGroupCultureDivergenceResult,
        )

        self.assertEqual(
            result.divergence,
            0.0,
        )

    def test_structural_transition_results_are_frozen(
        self
    ):
        result = self._split()

        with self.assertRaises(
            AttributeError
        ):
            result.reason = "changed"

        child_group = (
            result.daughter_group
        )

        divergence = (
            CatGroupCulturalInheritanceSystem(
                self.groups
            ).divergence(
                self.parent_group,
                child_group,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            divergence.divergence = 1.0


if __name__ == "__main__":
    unittest.main()
