import unittest

from cats.cat_family_system import (
    CatFamilySystem,
)
from cats.cat_maternal_care_result_state import (
    CatMaternalCareAssessment,
    CatMaternalCareDeniedResult,
    CatMaternalCareEvent,
    CatMaternalProtectionDeniedResult,
    CatMotherProtectedKittenEvent,
)
from cats.cat_maternal_care_system import (
    CatMaternalCareSystem,
)
from cats.cats import Cats
from cats.maternal_care_phase import (
    MaternalCarePhase,
)
from universe.universe import Universe


class CatMaternalCareResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.mother = self.cats.create_cat(
            name="result_mother",
            color="black",
            fur_length="short",
        )

        self.mother.sex = "female"

        self.kitten = self.cats.create_cat(
            name="result_kitten",
            color="white",
            fur_length="short",
        )

        self.kitten.mother_name = (
            self.mother.name
        )

        self.kitten.father_name = (
            "result_father"
        )

        CatFamilySystem(
            self.cats
        ).register_birth(
            mother=self.mother,
            kittens=[
                self.kitten
            ],
            cats=self.cats.cats,
        )

        self.care = CatMaternalCareSystem(
            self.cats
        )

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "name"
            ]

    def test_assessment_is_object(
        self
    ):
        result = self.care.evaluate(
            self.mother,
            self.kitten,
            age_days=5,
        )

        self.assertIsInstance(
            result,
            CatMaternalCareAssessment,
        )

        self.assertTrue(
            result.biological_child
        )

        self.assertIs(
            result.phase,
            MaternalCarePhase.NEONATAL,
        )

        self.assertTrue(
            result.nursing
        )

        self.assertTrue(
            result.warming
        )

        self.assert_object_only(
            result
        )

    def test_care_event_is_stored_as_detached_objects(
        self
    ):
        result = self.care.provide_care(
            self.mother,
            self.kitten,
            age_days=5,
            current_day=10,
        )

        mother_event = (
            self.mother.social_interactions[
                -1
            ]
        )

        kitten_event = (
            self.kitten.social_interactions[
                -1
            ]
        )

        emitted = self.cats.events[
            -1
        ]

        self.assertIsInstance(
            result,
            CatMaternalCareEvent,
        )

        self.assertIs(
            result.phase,
            MaternalCarePhase.NEONATAL,
        )

        self.assertIsInstance(
            result.actions,
            tuple,
        )

        self.assertIn(
            "nursing",
            result.actions,
        )

        for event in (
            mother_event,
            kitten_event,
            emitted,
        ):
            self.assertIsInstance(
                event,
                CatMaternalCareEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

        self.assertIsNot(
            mother_event,
            kitten_event,
        )

    def test_care_denial_is_object(
        self
    ):
        stranger = self.cats.create_cat(
            name="result_stranger",
            color="gray",
            fur_length="short",
        )

        result = self.care.provide_care(
            stranger,
            self.kitten,
            age_days=5,
        )

        self.assertIsInstance(
            result,
            CatMaternalCareDeniedResult,
        )

        self.assertFalse(
            result.provided
        )

        self.assertEqual(
            result.reason,
            "not_biological_mother",
        )

        self.assert_object_only(
            result
        )

    def test_protection_event_is_stored_as_detached_objects(
        self
    ):
        result = self.care.protect_from_threat(
            self.mother,
            self.kitten,
            threat={
                "name":
                    "cronenberg"
            },
            current_day=12,
        )

        mother_event = (
            self.mother.social_interactions[
                -1
            ]
        )

        kitten_event = (
            self.kitten.social_interactions[
                -1
            ]
        )

        emitted = self.cats.events[
            -1
        ]

        self.assertIsInstance(
            result,
            CatMotherProtectedKittenEvent,
        )

        self.assertTrue(
            result.protected
        )

        self.assertEqual(
            result.threat,
            "cronenberg",
        )

        for event in (
            mother_event,
            kitten_event,
            emitted,
        ):
            self.assertIsInstance(
                event,
                CatMotherProtectedKittenEvent,
            )

            self.assertEqual(
                event,
                result,
            )

            self.assertIsNot(
                event,
                result,
            )

            self.assert_object_only(
                event
            )

        self.assertIsNot(
            mother_event,
            kitten_event,
        )

    def test_protection_denial_is_object(
        self
    ):
        stranger = self.cats.create_cat(
            name="protection_stranger",
            color="gray",
            fur_length="short",
        )

        result = self.care.protect_from_threat(
            stranger,
            self.kitten,
            threat={
                "name":
                    "cronenberg"
            },
        )

        self.assertIsInstance(
            result,
            CatMaternalProtectionDeniedResult,
        )

        self.assertFalse(
            result.protected
        )

        self.assertEqual(
            result.reason,
            "not_biological_mother",
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
