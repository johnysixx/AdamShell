import unittest

from cats.cat_group_institution_maintenance_state import (
    CatGroupInstitutionMaintainedResult,
    CatGroupInstitutionMaintenanceDeniedResult,
)
from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupInstitutionMaintenanceObjectStateTests(
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
                "maintained"
            ]

    def test_unknown_institution_returns_denied_object(
        self
    ):
        result = (
            self.institutions.maintain(
                self.group_id,
                "missing_watch",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInstitutionMaintenanceDeniedResult,
        )

        self.assertFalse(
            result.maintained
        )

        self.assertEqual(
            result.name,
            "cat_group_institution_maintenance_denied",
        )

        self.assertEqual(
            result.reason,
            "unknown_institution",
        )

        self.assert_not_mapping(
            result
        )

    def test_missing_requirements_returns_weakened_object(
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

        result = (
            self.institutions.maintain(
                self.group_id,
                "night_watch",
            )
        )

        institution = (
            self.groups.groups[
                self.group_id
            ].institutions[
                "night_watch"
            ]
        )

        self.assertIsInstance(
            result,
            CatGroupInstitutionMaintainedResult,
        )

        self.assertTrue(
            result.maintained
        )

        self.assertEqual(
            result.name,
            "cat_group_institution_maintained",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.institution,
            "night_watch",
        )

        self.assertEqual(
            result.status,
            "weakened",
        )

        self.assertEqual(
            result.continuity,
            institution.continuity,
        )

        self.assertEqual(
            result.active,
            institution.active,
        )

        self.assert_not_mapping(
            result
        )

    def test_maintenance_result_tracks_strengthened_state(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "quiet_watch",
            "observe_group",
            roles=[],
            rituals=[],
        )

        institution = (
            self.groups.groups[
                self.group_id
            ].institutions[
                "quiet_watch"
            ]
        )

        before_generations = (
            institution.generations
        )

        result = (
            self.institutions.maintain(
                self.group_id,
                "quiet_watch",
            )
        )

        self.assertIsInstance(
            result,
            CatGroupInstitutionMaintainedResult,
        )

        self.assertEqual(
            result.status,
            "maintained",
        )

        self.assertEqual(
            result.continuity,
            1.0,
        )

        self.assertTrue(
            result.active
        )

        self.assertEqual(
            institution.generations,
            before_generations
            + 1,
        )

    def test_repeated_weakening_can_deactivate_institution(
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

        result = None

        for _ in range(
            7
        ):
            result = (
                self.institutions.maintain(
                    self.group_id,
                    "night_watch",
                )
            )

        institution = (
            self.groups.groups[
                self.group_id
            ].institutions[
                "night_watch"
            ]
        )

        self.assertIsInstance(
            result,
            CatGroupInstitutionMaintainedResult,
        )

        self.assertEqual(
            result.status,
            "weakened",
        )

        self.assertFalse(
            result.active
        )

        self.assertFalse(
            institution.active
        )

        self.assertEqual(
            result.continuity,
            institution.continuity,
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.institutions.maintain(
                self.group_id,
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.reason = "changed"

        self.institutions.establish(
            self.group_id,
            "quiet_watch",
            "observe_group",
            roles=[],
            rituals=[],
        )

        maintained = (
            self.institutions.maintain(
                self.group_id,
                "quiet_watch",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            maintained.status = "changed"


if __name__ == "__main__":
    unittest.main()
