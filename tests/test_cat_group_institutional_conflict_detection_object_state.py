import unittest

from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_institutional_conflict_detection_state import (
    CatInstitutionConflictDetectedResult,
    CatInstitutionConflictDetectionDeniedResult,
)
from cats.cat_group_institutional_conflict_system import (
    CatGroupInstitutionalConflictSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupInstitutionalConflictDetectionObjectStateTests(
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
                "conflict"
            ]

    def test_unknown_institution_returns_denied_object(
        self
    ):
        result = (
            self.conflicts.detect(
                self.group_id,
                "missing_first",
                "missing_second",
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionConflictDetectionDeniedResult,
        )

        self.assertFalse(
            result.conflict
        )

        self.assertEqual(
            result.name,
            "cat_institution_conflict_detection_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_institution",
        )

        self.assert_not_mapping(
            result
        )

    def test_shared_role_returns_friction_object(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "night_watch",
            "protect_sleeping_group",
            roles=[
                "guardian"
            ],
            rituals=[
                "evening_patrol"
            ],
        )

        self.institutions.establish(
            self.group_id,
            "door_watch",
            "control_box_door",
            roles=[
                "guardian"
            ],
            rituals=[
                "door_patrol"
            ],
        )

        result = (
            self.conflicts.detect(
                self.group_id,
                "night_watch",
                "door_watch",
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionConflictDetectedResult,
        )

        self.assertTrue(
            result.conflict
        )

        self.assertEqual(
            result.name,
            "cat_institution_conflict_detected",
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
            result.shared_roles,
            (
                "guardian",
            ),
        )

        self.assertEqual(
            result.shared_rituals,
            (),
        )

        self.assertTrue(
            result.different_purpose
        )

        self.assertEqual(
            result.score,
            0.45,
        )

        self.assertEqual(
            result.status,
            "institutional_friction",
        )

        self.assert_not_mapping(
            result
        )

    def test_shared_role_and_ritual_can_reach_conflict(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "first_watch",
            "protect_sleeping_group",
            roles=[
                "guardian"
            ],
            rituals=[
                "evening_patrol"
            ],
        )

        self.institutions.establish(
            self.group_id,
            "second_watch",
            "control_box_door",
            roles=[
                "guardian"
            ],
            rituals=[
                "evening_patrol"
            ],
        )

        result = (
            self.conflicts.detect(
                self.group_id,
                "first_watch",
                "second_watch",
            )
        )

        self.assertTrue(
            result.conflict
        )

        self.assertEqual(
            result.shared_roles,
            (
                "guardian",
            ),
        )

        self.assertEqual(
            result.shared_rituals,
            (
                "evening_patrol",
            ),
        )

        self.assertEqual(
            result.score,
            0.6,
        )

        self.assertEqual(
            result.status,
            "institutional_conflict",
        )

    def test_unrelated_institutions_are_compatible(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "night_watch",
            "protect_group",
            roles=[
                "guardian"
            ],
            rituals=[
                "evening_patrol"
            ],
        )

        self.institutions.establish(
            self.group_id,
            "story_circle",
            "share_stories",
            roles=[
                "storyteller"
            ],
            rituals=[
                "story_night"
            ],
        )

        result = (
            self.conflicts.detect(
                self.group_id,
                "night_watch",
                "story_circle",
            )
        )

        self.assertIsInstance(
            result,
            CatInstitutionConflictDetectedResult,
        )

        self.assertFalse(
            result.conflict
        )

        self.assertEqual(
            result.shared_roles,
            (),
        )

        self.assertEqual(
            result.shared_rituals,
            (),
        )

        self.assertEqual(
            result.score,
            0.0,
        )

        self.assertEqual(
            result.status,
            "institutionally_compatible",
        )

    def test_collections_are_immutable_tuples(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "first_watch",
            "first_purpose",
            roles=[
                "guardian",
                "observer",
            ],
            rituals=[
                "dawn_watch",
                "evening_patrol",
            ],
        )

        self.institutions.establish(
            self.group_id,
            "second_watch",
            "second_purpose",
            roles=[
                "observer",
                "guardian",
            ],
            rituals=[
                "evening_patrol",
                "dawn_watch",
            ],
        )

        result = (
            self.conflicts.detect(
                self.group_id,
                "first_watch",
                "second_watch",
            )
        )

        self.assertIsInstance(
            result.shared_roles,
            tuple,
        )

        self.assertIsInstance(
            result.shared_rituals,
            tuple,
        )

        self.assertEqual(
            result.shared_roles,
            (
                "guardian",
                "observer",
            ),
        )

        self.assertEqual(
            result.shared_rituals,
            (
                "dawn_watch",
                "evening_patrol",
            ),
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.conflicts.detect(
                self.group_id,
                "missing",
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        self.institutions.establish(
            self.group_id,
            "first_watch",
            "first",
            roles=[],
            rituals=[],
        )

        self.institutions.establish(
            self.group_id,
            "second_watch",
            "second",
            roles=[],
            rituals=[],
        )

        detected = (
            self.conflicts.detect(
                self.group_id,
                "first_watch",
                "second_watch",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            detected.status = "changed"


if __name__ == "__main__":
    unittest.main()
