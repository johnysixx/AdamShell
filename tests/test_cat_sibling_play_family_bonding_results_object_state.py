import unittest

from cats.cat_family_bonding_result_state import (
    CatFamilyBondEvaluationResult,
    CatFamilyBondFormedEvent,
    CatFamilyBondNotFormedResult,
)
from cats.cat_family_bonding_system import (
    CatFamilyBondingSystem,
)
from cats.cat_family_system import (
    CatFamilySystem,
)
from cats.cat_sibling_play_result_state import (
    CatSiblingPlayDeniedResult,
    CatSiblingPlayEvaluationResult,
    CatSiblingPlayEvent,
)
from cats.cat_sibling_play_system import (
    CatSiblingPlaySystem,
)
from cats.cats import Cats
from universe.universe import Universe


class CatSiblingPlayFamilyBondingResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.mother = self.cats.create_cat(
            name="play_mother",
            color="black",
            fur_length="short",
        )

        self.mother.sex = "female"

        self.first = self.cats.create_cat(
            name="play_first",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="play_second",
            color="white",
            fur_length="short",
        )

        for kitten in (
            self.first,
            self.second,
        ):
            kitten.mother_name = (
                self.mother.name
            )

            kitten.father_name = (
                "play_father"
            )

        CatFamilySystem(
            self.cats
        ).register_birth(
            mother=self.mother,
            kittens=[
                self.first,
                self.second,
            ],
            cats=self.cats.cats,
        )

        self.play = CatSiblingPlaySystem(
            self.cats
        )

        self.bonding = (
            CatFamilyBondingSystem(
                self.cats
            )
        )

    def assert_object_only(
        self,
        value,
    ):
        for method_name in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
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
                "name"
            ]

    def test_play_evaluation_is_object(
        self
    ):
        result = self.play.can_play(
            self.first,
            self.second,
            age_days=30,
        )

        self.assertIsInstance(
            result,
            CatSiblingPlayEvaluationResult,
        )

        self.assertTrue(
            result.allowed
        )

        self.assertEqual(
            result.relation,
            "sibling_littermate",
        )

        self.assert_object_only(
            result
        )

    def test_play_denial_is_object(
        self
    ):
        stranger = self.cats.create_cat(
            name="play_stranger",
            color="gray",
            fur_length="short",
        )

        result = self.play.play(
            self.first,
            stranger,
            age_days=30,
        )

        self.assertIsInstance(
            result,
            CatSiblingPlayDeniedResult,
        )

        self.assertFalse(
            result.played
        )

        self.assertFalse(
            result.allowed
        )

        self.assert_object_only(
            result
        )

    def test_play_event_is_stored_as_detached_objects(
        self
    ):
        result = self.play.play(
            self.first,
            self.second,
            age_days=30,
            current_day=200,
        )

        first_event = (
            self.first.social_interactions[
                -1
            ]
        )

        second_event = (
            self.second.social_interactions[
                -1
            ]
        )

        emitted = (
            self.cats.events[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatSiblingPlayEvent,
        )

        self.assertTrue(
            result.played
        )

        for event in (
            first_event,
            second_event,
            emitted,
        ):
            self.assertIsInstance(
                event,
                CatSiblingPlayEvent,
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
            first_event,
            second_event,
        )

    def test_family_bond_evaluation_is_object(
        self
    ):
        for _ in range(3):
            self.play.play(
                self.first,
                self.second,
                age_days=30,
            )

        result = self.bonding.evaluate(
            self.first,
            self.second,
        )

        self.assertIsInstance(
            result,
            CatFamilyBondEvaluationResult,
        )

        self.assertTrue(
            result.related
        )

        self.assertTrue(
            result.eligible
        )

        self.assertEqual(
            result.play_events,
            3,
        )

        self.assert_object_only(
            result
        )

    def test_family_bond_denial_is_object(
        self
    ):
        result = self.bonding.form_bond(
            self.first,
            self.second,
        )

        self.assertIsInstance(
            result,
            CatFamilyBondNotFormedResult,
        )

        self.assertFalse(
            result.formed
        )

        self.assertEqual(
            result.reason,
            "family_bond_requirements_not_met",
        )

        self.assert_object_only(
            result
        )

    def test_family_bond_event_is_stored_as_detached_objects(
        self
    ):
        for _ in range(3):
            self.play.play(
                self.first,
                self.second,
                age_days=30,
            )

        result = self.bonding.form_bond(
            self.first,
            self.second,
        )

        first_event = (
            self.first.social_interactions[
                -1
            ]
        )

        second_event = (
            self.second.social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatFamilyBondFormedEvent,
        )

        self.assertTrue(
            result.formed
        )

        for event in (
            first_event,
            second_event,
        ):
            self.assertIsInstance(
                event,
                CatFamilyBondFormedEvent,
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
            first_event,
            second_event,
        )


if __name__ == "__main__":
    unittest.main()
