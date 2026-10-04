import unittest

from cats.cat_culture_objects import (
    CatInstitutionConflict,
)
from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_institutional_conflict_escalation_state import (
    CatGroupInstitutionalConflictEvent,
    CatInstitutionConflictEscalationDeniedResult,
)
from cats.cat_group_institutional_conflict_system import (
    CatGroupInstitutionalConflictSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupInstitutionalConflictEscalationObjectStateTests(
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

    def create_institutions(self):
        self.institutions.establish(
            self.group_id,
            "night_watch",
            "protect_sleeping_group",
            roles=[
                "guardian"
            ],
            rituals=[],
        )

        self.institutions.establish(
            self.group_id,
            "door_watch",
            "control_box_door",
            roles=[
                "guardian"
            ],
            rituals=[],
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
                "escalated"
            ]

    def test_unknown_institution_returns_denied_object(
        self
    ):
        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        conflict_count_before = len(
            group.institution_conflicts
        )

        history_count_before = len(
            group.history
        )

        result = (
            self.conflicts.escalate(
                self.group_id,
                "missing_first",
                "missing_second",
                issue="guardian_attention",
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionConflictEscalationDeniedResult,
        )

        self.assertFalse(
            result.escalated
        )

        self.assertEqual(
            result.name,
            "cat_institution_conflict_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_institution",
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

        self.assertEqual(
            len(
                group.institution_conflicts
            ),
            conflict_count_before,
        )

        self.assertEqual(
            len(
                group.history
            ),
            history_count_before,
        )

    def test_escalate_returns_event_object(
        self
    ):
        self.create_institutions()

        result = (
            self.conflicts.escalate(
                self.group_id,
                "night_watch",
                "door_watch",
                issue="guardian_attention",
                intensity=0.8,
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInstitutionalConflictEvent,
        )

        self.assertTrue(
            result.escalated
        )

        self.assertEqual(
            result.name,
            "cat_group_institutional_conflict",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.first_institution,
            "night_watch",
        )

        self.assertEqual(
            result.second_institution,
            "door_watch",
        )

        self.assertEqual(
            result.issue,
            "guardian_attention",
        )

        self.assertEqual(
            result.intensity,
            0.8,
        )

        self.assertTrue(
            result.conflict_id.startswith(
                "institution_conflict_"
            )
        )

        self.assert_not_mapping(
            result
        )

    def test_escalate_creates_conflict_object_and_weakens_institutions(
        self
    ):
        self.create_institutions()

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

        result = (
            self.conflicts.escalate(
                self.group_id,
                "night_watch",
                "door_watch",
                issue="guardian_attention",
                intensity=0.5,
            )
        )

        stored = (
            group.institution_conflicts[
                result.conflict_id
            ]
        )

        self.assertIsInstance(
            stored,
            CatInstitutionConflict,
        )

        self.assertEqual(
            stored.id,
            result.conflict_id,
        )

        self.assertEqual(
            stored.first_institution,
            result.first_institution,
        )

        self.assertEqual(
            stored.second_institution,
            result.second_institution,
        )

        self.assertEqual(
            stored.issue,
            result.issue,
        )

        self.assertEqual(
            stored.intensity,
            result.intensity,
        )

        self.assertFalse(
            stored.resolved
        )

        self.assertIsNone(
            stored.mediator
        )

        self.assertAlmostEqual(
            first.continuity,
            0.9,
        )

        self.assertAlmostEqual(
            second.continuity,
            0.9,
        )

    def test_histories_remain_serialized_boundaries(
        self
    ):
        self.create_institutions()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        result = (
            self.conflicts.escalate(
                self.group_id,
                "night_watch",
                "door_watch",
                issue="guardian_attention",
                intensity=0.4,
            )
        )

        conflict = (
            group.institution_conflicts[
                result.conflict_id
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

        self.assertIsInstance(
            conflict_event,
            dict,
        )

        self.assertIsInstance(
            group_event,
            dict,
        )

        self.assertEqual(
            conflict_event,
            result.to_dict(),
        )

        self.assertEqual(
            group_event,
            result.to_dict(),
        )

        self.assertIsNot(
            conflict_event,
            group_event,
        )

    def test_history_snapshots_are_detached_from_event_and_each_other(
        self
    ):
        self.create_institutions()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        result = (
            self.conflicts.escalate(
                self.group_id,
                "night_watch",
                "door_watch",
                issue="guardian_attention",
                intensity=0.4,
            )
        )

        conflict = (
            group.institution_conflicts[
                result.conflict_id
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

        conflict_event[
            "issue"
        ] = "changed"

        self.assertEqual(
            result.issue,
            "guardian_attention",
        )

        self.assertEqual(
            group_event[
                "issue"
            ],
            "guardian_attention",
        )

        serialized = (
            result.to_dict()
        )

        serialized[
            "issue"
        ] = "also_changed"

        self.assertEqual(
            result.issue,
            "guardian_attention",
        )

        self.assertEqual(
            group_event[
                "issue"
            ],
            "guardian_attention",
        )

    def test_intensity_is_clamped_before_result_and_state(
        self
    ):
        self.create_institutions()

        group = (
            self.groups.groups[
                self.group_id
            ]
        )

        result = (
            self.conflicts.escalate(
                self.group_id,
                "night_watch",
                "door_watch",
                issue="guardian_attention",
                intensity=2.0,
            )
        )

        conflict = (
            group.institution_conflicts[
                result.conflict_id
            ]
        )

        self.assertEqual(
            result.intensity,
            1.0,
        )

        self.assertEqual(
            conflict.intensity,
            1.0,
        )

        self.assertAlmostEqual(
            group.institutions[
                "night_watch"
            ].continuity,
            0.8,
        )

        self.assertAlmostEqual(
            group.institutions[
                "door_watch"
            ].continuity,
            0.8,
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.conflicts.escalate(
                self.group_id,
                "missing",
                "missing",
                issue="test",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        self.create_institutions()

        event = (
            self.conflicts.escalate(
                self.group_id,
                "night_watch",
                "door_watch",
                issue="guardian_attention",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            event.issue = "changed"


if __name__ == "__main__":
    unittest.main()
