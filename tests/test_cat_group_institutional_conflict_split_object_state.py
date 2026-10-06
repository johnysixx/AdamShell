import unittest

from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_institutional_conflict_split_state import (
    CatInstitutionalSplitResult,
    CatInstitutionSplitDeniedResult,
)
from cats.cat_group_institutional_conflict_system import (
    CatGroupInstitutionalConflictSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupInstitutionalConflictSplitObjectStateTests(
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

    def create_conflict(
        self,
        intensity,
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
                "split"
            ]

    def test_unknown_conflict_returns_denied_object(
        self
    ):
        result = (
            self.conflicts.institutional_split(
                self.group_id,
                "missing_conflict",
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionSplitDeniedResult,
        )

        self.assertFalse(
            result.split
        )

        self.assertEqual(
            result.name,
            "cat_institution_split_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_conflict",
        )

        self.assert_not_mapping(
            result
        )

    def test_low_intensity_conflict_returns_denied_object(
        self
    ):
        created = (
            self.create_conflict(
                intensity=0.5
            )
        )

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

        first_before = (
            first.continuity
        )

        second_before = (
            second.continuity
        )

        result = (
            self.conflicts.institutional_split(
                self.group_id,
                created.conflict_id,
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionSplitDeniedResult,
        )

        self.assertFalse(
            result.split
        )

        self.assertEqual(
            result.reason,
            "conflict_not_severe_enough",
        )

        self.assertEqual(
            first.continuity,
            first_before,
        )

        self.assertEqual(
            second.continuity,
            second_before,
        )

        self.assert_not_mapping(
            result
        )

    def test_severe_conflict_returns_split_object(
        self
    ):
        created = (
            self.create_conflict(
                intensity=0.9
            )
        )

        result = (
            self.conflicts.institutional_split(
                self.group_id,
                created.conflict_id,
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionalSplitResult,
        )

        self.assertTrue(
            result.split
        )

        self.assertEqual(
            result.name,
            "cat_institutional_split",
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
            result.institutions,
            (
                "night_watch",
                "door_watch",
            ),
        )

        self.assertIsInstance(
            result.institutions,
            tuple,
        )

        self.assert_not_mapping(
            result
        )

    def test_split_updates_institutions_through_attributes(
        self
    ):
        created = (
            self.create_conflict(
                intensity=0.9
            )
        )

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
            0.82,
        )

        self.assertAlmostEqual(
            second.continuity,
            0.82,
        )

        result = (
            self.conflicts.institutional_split(
                self.group_id,
                created.conflict_id,
            )
        )

        self.assertTrue(
            result.split
        )

        self.assertAlmostEqual(
            first.continuity,
            0.57,
        )

        self.assertAlmostEqual(
            second.continuity,
            0.57,
        )

    def test_continuity_does_not_drop_below_zero(
        self
    ):
        created = (
            self.create_conflict(
                intensity=1.0
            )
        )

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

        first.continuity = 0.1
        second.continuity = 0.2

        result = (
            self.conflicts.institutional_split(
                self.group_id,
                created.conflict_id,
            )
        )

        self.assertTrue(
            result.split
        )

        self.assertEqual(
            first.continuity,
            0.0,
        )

        self.assertEqual(
            second.continuity,
            0.0,
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.conflicts.institutional_split(
                self.group_id,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        created = (
            self.create_conflict(
                intensity=0.9
            )
        )

        result = (
            self.conflicts.institutional_split(
                self.group_id,
                created.conflict_id,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            result.conflict_id = "changed"

        with self.assertRaises(
            AttributeError
        ):
            result.institutions = (
                "changed",
            )


if __name__ == "__main__":
    unittest.main()
