import unittest

from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_institutional_conflict_mediation_state import (
    CatInstitutionConflictMediatedEvent,
    CatInstitutionMediationDeniedResult,
)
from cats.cat_group_institutional_conflict_system import (
    CatGroupInstitutionalConflictSystem,
)
from cats.cat_group_role_system import (
    CatGroupRoleSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupInstitutionalConflictMediationObjectStateTests(
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

        self.mediator = (
            self.cats.create_cat(
                name="mediator_cat",
                color="gray",
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
                self.first,
                name="bar_cats",
            )
        )

        self.group_id = (
            created_group.group_id
        )

        self.groups.add_member(
            self.group_id,
            self.second,
            self.cats.cats,
        )

        self.groups.add_member(
            self.group_id,
            self.mediator,
            self.cats.cats,
        )

        self.institutions = (
            CatGroupInstitutionSystem(
                self.groups
            )
        )

        self.conflicts = (
            CatGroupInstitutionalConflictSystem(
                self.groups
            )
        )

        self.roles = (
            CatGroupRoleSystem(
                self.groups
            )
        )

    def create_conflict(
        self,
        intensity=0.4,
    ):
        self.institutions.establish(
            self.group_id,
            "night_watch",
            "protect_sleeping_group",
            roles=[],
            rituals=[],
        )

        self.institutions.establish(
            self.group_id,
            "door_watch",
            "control_box_door",
            roles=[],
            rituals=[],
        )

        return (
            self.conflicts.escalate(
                self.group_id,
                "night_watch",
                "door_watch",
                issue="guardian_attention",
                intensity=intensity,
            )
        )

    def make_mediator(self):
        self.mediator.personality.traits.sociability = (
            1.0
        )

        self.mediator.group.influence = (
            1.0
        )

        assigned = (
            self.roles.assign(
                self.group_id,
                self.mediator,
                "mediator",
            )
        )

        self.assertTrue(
            assigned.assigned
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
                "mediated"
            ]

    def test_unknown_conflict_returns_denied_object(
        self
    ):
        result = (
            self.conflicts.mediate(
                self.group_id,
                "missing_conflict",
                self.mediator,
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionMediationDeniedResult,
        )

        self.assertFalse(
            result.mediated
        )

        self.assertEqual(
            result.name,
            "cat_institution_mediation_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_conflict",
        )

        self.assertFalse(
            hasattr(
                result,
                "to_dict",
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_non_mediator_returns_denied_object_without_mutation(
        self
    ):
        created = (
            self.create_conflict(
                intensity=0.4
            )
        )

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        conflict = (
            group.institution_conflicts[
                created.conflict_id
            ]
        )

        intensity_before = (
            conflict.intensity
        )

        history_before = len(
            conflict.history
        )

        group_history_before = len(
            group.history
        )

        result = (
            self.conflicts.mediate(
                self.group_id,
                created.conflict_id,
                self.mediator,
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionMediationDeniedResult,
        )

        self.assertEqual(
            result.reason,
            "cat_not_mediator",
        )

        self.assertFalse(
            result.mediated
        )

        self.assertEqual(
            conflict.intensity,
            intensity_before,
        )

        self.assertIsNone(
            conflict.mediator
        )

        self.assertFalse(
            conflict.resolved
        )

        self.assertEqual(
            len(
                conflict.history
            ),
            history_before,
        )

        self.assertEqual(
            len(
                group.history
            ),
            group_history_before,
        )

    def test_mediate_returns_event_object(
        self
    ):
        created = (
            self.create_conflict(
                intensity=0.4
            )
        )

        self.make_mediator()

        result = (
            self.conflicts.mediate(
                self.group_id,
                created.conflict_id,
                self.mediator,
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionConflictMediatedEvent,
        )

        self.assertTrue(
            result.mediated
        )

        self.assertEqual(
            result.name,
            "cat_institution_conflict_mediated",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.conflict_id,
            created.conflict_id,
        )

        self.assertEqual(
            result.mediator,
            self.mediator.name,
        )

        self.assertTrue(
            result.resolved
        )

        self.assertEqual(
            result.intensity,
            0.0,
        )

        self.assert_not_mapping(
            result
        )

    def test_mediation_updates_same_conflict_object(
        self
    ):
        created = (
            self.create_conflict(
                intensity=0.4
            )
        )

        self.make_mediator()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        stored = (
            group.institution_conflicts[
                created.conflict_id
            ]
        )

        result = (
            self.conflicts.mediate(
                self.group_id,
                created.conflict_id,
                self.mediator,
            )
        )

        current = (
            group.institution_conflicts[
                created.conflict_id
            ]
        )

        self.assertIs(
            current,
            stored,
        )

        self.assertEqual(
            current.mediator,
            result.mediator,
        )

        self.assertEqual(
            current.intensity,
            result.intensity,
        )

        self.assertEqual(
            current.resolved,
            result.resolved,
        )

    def test_resolved_mediation_restores_institutions(
        self
    ):
        created = (
            self.create_conflict(
                intensity=0.4
            )
        )

        self.make_mediator()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        first = (
            group.institutions[
                "night_watch"
            ]
        )

        second = (
            group.institutions[
                "door_watch"
            ]
        )

        self.assertAlmostEqual(
            first.continuity,
            0.92,
        )

        self.assertAlmostEqual(
            second.continuity,
            0.92,
        )

        result = (
            self.conflicts.mediate(
                self.group_id,
                created.conflict_id,
                self.mediator,
            )
        )

        self.assertTrue(
            result.resolved
        )

        self.assertEqual(
            first.continuity,
            1.0,
        )

        self.assertEqual(
            second.continuity,
            1.0,
        )

    def test_histories_store_detached_event_objects(
        self
    ):
        created = self.create_conflict(
            intensity=0.4
        )

        self.make_mediator()

        group = self.groups.groups[
            self.group_id
        ]

        result = self.conflicts.mediate(
            self.group_id,
            created.conflict_id,
            self.mediator,
        )

        conflict = (
            group.institution_conflicts[
                created.conflict_id
            ]
        )

        conflict_event = (
            conflict.history[
                -1
            ]
        )

        group_event = (
            group.history[
                -1
            ]
        )

        for event in (
            conflict_event,
            group_event,
        ):
            self.assertIsInstance(
                event,
                CatInstitutionConflictMediatedEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assertFalse(
                hasattr(
                    event,
                    "to_dict",
                )
            )

        self.assertIsNot(
            conflict_event,
            group_event,
        )

    def test_history_events_are_frozen_and_detached(
        self
    ):
        created = self.create_conflict(
            intensity=0.4
        )

        self.make_mediator()

        group = self.groups.groups[
            self.group_id
        ]

        result = self.conflicts.mediate(
            self.group_id,
            created.conflict_id,
            self.mediator,
        )

        conflict = (
            group.institution_conflicts[
                created.conflict_id
            ]
        )

        conflict_event = (
            conflict.history[
                -1
            ]
        )

        group_event = (
            group.history[
                -1
            ]
        )

        self.assertIsNot(
            conflict_event,
            group_event,
        )

        with self.assertRaises(
            AttributeError
        ):
            conflict_event.mediator = (
                "changed"
            )

        self.assertEqual(
            result.mediator,
            self.mediator.name,
        )

        self.assertEqual(
            group_event.mediator,
            self.mediator.name,
        )

        self.assertTrue(
            group_event.resolved
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.conflicts.mediate(
                self.group_id,
                "missing",
                self.mediator,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        created = (
            self.create_conflict(
                intensity=0.4
            )
        )

        self.make_mediator()

        event = (
            self.conflicts.mediate(
                self.group_id,
                created.conflict_id,
                self.mediator,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            event.resolved = False


if __name__ == "__main__":
    unittest.main()
