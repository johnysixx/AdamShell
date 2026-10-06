import unittest

from cats.cat_group_institution_establishment_state import (
    CatGroupInstitutionEstablishedEvent,
)
from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupInstitutionEstablishmentObjectStateTests(
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

    def test_establish_returns_event_object(
        self
    ):
        result = (
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
        )

        self.assertIsInstance(
            result,
            CatGroupInstitutionEstablishedEvent,
        )

        self.assertTrue(
            result.established
        )

        self.assertEqual(
            result.name,
            "cat_group_institution_established",
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
            result.purpose,
            "protect_sleeping_group",
        )

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
                "established"
            ]

    def test_establishment_creates_institution_object(
        self
    ):
        result = (
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
        )

        institution = (
            self.groups.groups[
                self.group_id
            ].institutions[
                result.institution
            ]
        )

        self.assertEqual(
            institution.name,
            "night_watch",
        )

        self.assertEqual(
            institution.purpose,
            "protect_group",
        )

        self.assertEqual(
            institution.roles,
            [
                "guardian"
            ],
        )

        self.assertEqual(
            institution.rituals,
            [
                "evening_patrol"
            ],
        )

        self.assertEqual(
            institution.continuity,
            1.0,
        )

        self.assertEqual(
            institution.generations,
            0,
        )

        self.assertTrue(
            institution.active
        )

    def test_history_remains_serialized_boundary(
        self
    ):
        result = (
            self.institutions.establish(
                self.group_id,
                "kitten_guard",
                "protect_kittens",
                roles=[],
                rituals=[],
            )
        )

        history_event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertIsInstance(
            history_event,
            dict,
        )

        self.assertEqual(
            history_event,
            result.to_dict(),
        )

        self.assertEqual(
            history_event[
                "institution"
            ],
            result.institution,
        )

    def test_serialized_snapshot_is_detached(
        self
    ):
        result = (
            self.institutions.establish(
                self.group_id,
                "door_watch",
                "control_box_door",
                roles=[],
                rituals=[],
            )
        )

        serialized = (
            result.to_dict()
        )

        serialized[
            "institution"
        ] = "changed"

        history_event = (
            self.groups.groups[
                self.group_id
            ].history[
                -1
            ]
        )

        self.assertEqual(
            result.institution,
            "door_watch",
        )

        self.assertEqual(
            history_event[
                "institution"
            ],
            "door_watch",
        )


if __name__ == "__main__":
    unittest.main()
