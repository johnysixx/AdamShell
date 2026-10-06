import unittest

from cats.cat_group_institution_system import (
    CatGroupInstitutionSystem,
)
from cats.cat_group_norm_institution_link_state import (
    CatNormAttachedToInstitutionResult,
    CatNormInstitutionLinkDeniedResult,
)
from cats.cat_group_norm_institution_system import (
    CatGroupNormInstitutionSystem,
)
from cats.cat_group_norm_system import (
    CatGroupNormSystem,
)
from cats.cat_group_system import (
    CatGroupSystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatGroupNormInstitutionLinkObjectStateTests(
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

        self.norms = (
            CatGroupNormSystem(
                self.groups
            )
        )

        self.links = (
            CatGroupNormInstitutionSystem(
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
                "linked"
            ]

    def test_unknown_institution_returns_denied_object(
        self
    ):
        norm = (
            self.norms.define(
                self.group_id,
                "protect_kittens",
                "protective",
                {
                    "target": "kitten"
                },
                importance=0.9,
            )
        )

        result = (
            self.links.attach_norm(
                self.group_id,
                "missing_institution",
                norm.norm_id,
            )
        )

        self.assertIsInstance(
            result,
            CatNormInstitutionLinkDeniedResult,
        )

        self.assertFalse(
            result.linked
        )

        self.assertEqual(
            result.name,
            "cat_norm_institution_link_denied",
        )

        self.assert_not_mapping(
            result
        )

    def test_unknown_norm_returns_denied_object(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "kitten_guard",
            "protect_kittens",
            roles=[],
            rituals=[],
        )

        result = (
            self.links.attach_norm(
                self.group_id,
                "kitten_guard",
                "missing_norm",
            )
        )

        self.assertIsInstance(
            result,
            CatNormInstitutionLinkDeniedResult,
        )

        self.assertFalse(
            result.linked
        )

        self.assert_not_mapping(
            result
        )

    def test_attach_returns_object_result(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "kitten_guard",
            "protect_kittens",
            roles=[],
            rituals=[],
        )

        norm = (
            self.norms.define(
                self.group_id,
                "protect_kittens",
                "protective",
                {
                    "target": "kitten"
                },
                importance=0.9,
            )
        )

        result = (
            self.links.attach_norm(
                self.group_id,
                "kitten_guard",
                norm.norm_id,
            )
        )

        self.assertIsInstance(
            result,
            CatNormAttachedToInstitutionResult,
        )

        self.assertTrue(
            result.linked
        )

        self.assertEqual(
            result.name,
            "cat_norm_attached_to_institution",
        )

        self.assertEqual(
            result.group_id,
            self.group_id,
        )

        self.assertEqual(
            result.institution,
            "kitten_guard",
        )

        self.assertEqual(
            result.norm_id,
            norm.norm_id,
        )

        self.assert_not_mapping(
            result
        )

    def test_attach_stores_norm_on_institution(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "kitten_guard",
            "protect_kittens",
            roles=[],
            rituals=[],
        )

        norm = (
            self.norms.define(
                self.group_id,
                "protect_kittens",
                "protective",
                {
                    "target": "kitten"
                },
                importance=0.9,
            )
        )

        result = (
            self.links.attach_norm(
                self.group_id,
                "kitten_guard",
                norm.norm_id,
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
            institution.norms,
            [
                result.norm_id
            ],
        )

    def test_repeated_attach_does_not_duplicate_norm(
        self
    ):
        self.institutions.establish(
            self.group_id,
            "kitten_guard",
            "protect_kittens",
            roles=[],
            rituals=[],
        )

        norm = (
            self.norms.define(
                self.group_id,
                "protect_kittens",
                "protective",
                {
                    "target": "kitten"
                },
                importance=0.9,
            )
        )

        first = (
            self.links.attach_norm(
                self.group_id,
                "kitten_guard",
                norm.norm_id,
            )
        )

        second = (
            self.links.attach_norm(
                self.group_id,
                "kitten_guard",
                norm.norm_id,
            )
        )

        institution = (
            self.groups.groups[
                self.group_id
            ].institutions[
                "kitten_guard"
            ]
        )

        self.assertTrue(
            first.linked
        )

        self.assertTrue(
            second.linked
        )

        self.assertEqual(
            institution.norms,
            [
                norm.norm_id
            ],
        )

    def test_results_are_immutable(
        self
    ):
        denied = (
            self.links.attach_norm(
                self.group_id,
                "missing",
                "missing",
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            denied.linked = True

        self.institutions.establish(
            self.group_id,
            "kitten_guard",
            "protect_kittens",
            roles=[],
            rituals=[],
        )

        norm = (
            self.norms.define(
                self.group_id,
                "protect_kittens",
                "protective",
                {
                    "target": "kitten"
                },
                importance=0.9,
            )
        )

        linked = (
            self.links.attach_norm(
                self.group_id,
                "kitten_guard",
                norm.norm_id,
            )
        )

        with self.assertRaises(
            AttributeError
        ):
            linked.norm_id = "changed"


if __name__ == "__main__":
    unittest.main()
