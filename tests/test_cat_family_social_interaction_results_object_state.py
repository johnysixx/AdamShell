import unittest

from cats.cat_family_system import (
    CatFamilySystem,
)
from cats.cat_human_bond_result_state import (
    CatHumanBondEvaluationResult,
    CatHumanInteractionRememberedEvent,
)
from cats.cat_human_bond_system import (
    CatHumanBondSystem,
)
from cats.cat_meow_invitation_system import (
    CatMeowInvitationSystem,
)
from cats.cat_parental_teaching_result_state import (
    CatParentalTeachingDeniedResult,
    CatParentTaughtKittenEvent,
)
from cats.cat_parental_teaching_system import (
    CatParentalTeachingSystem,
)
from cats.cat_sibling_rivalry_result_state import (
    CatSiblingReconciliationDeniedResult,
    CatSiblingRivalryDeniedResult,
    CatSiblingRivalryEvent,
    CatSiblingsReconciledEvent,
)
from cats.cat_sibling_rivalry_system import (
    CatSiblingRivalrySystem,
)
from cats.cats import Cats
from universe.universe import Universe


class Human:

    def __init__(
        self,
        name,
    ):
        self.name = name


class CatFamilySocialInteractionResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.mother = self.cats.create_cat(
            name="object_mother",
            color="black",
            fur_length="short",
        )

        self.mother.sex = "female"

        self.father = self.cats.create_cat(
            name="object_father",
            color="orange",
            fur_length="short",
        )

        self.father.sex = "male"

        self.first = self.cats.create_cat(
            name="object_kitten_1",
            color="black",
            fur_length="short",
        )

        self.second = self.cats.create_cat(
            name="object_kitten_2",
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
                self.father.name
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

    def test_sibling_rivalry_returns_and_stores_objects(
        self
    ):
        rivalry = (
            CatSiblingRivalrySystem(
                self.cats
            )
        )

        result = rivalry.compete(
            self.first,
            self.second,
            resource="window",
            intensity=0.8,
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
            CatSiblingRivalryEvent,
        )

        self.assertTrue(
            result.competed
        )

        for event in (
            first_event,
            second_event,
        ):
            self.assertIsInstance(
                event,
                CatSiblingRivalryEvent,
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

    def test_sibling_rivalry_denial_is_object(
        self
    ):
        stranger = self.cats.create_cat(
            name="object_stranger",
            color="gray",
            fur_length="short",
        )

        result = CatSiblingRivalrySystem(
            self.cats
        ).compete(
            self.first,
            stranger,
            resource="food",
        )

        self.assertIsInstance(
            result,
            CatSiblingRivalryDeniedResult,
        )

        self.assertFalse(
            result.competed
        )

        self.assertEqual(
            result.reason,
            "not_siblings",
        )

        self.assert_object_only(
            result
        )

    def test_sibling_reconciliation_returns_and_stores_objects(
        self
    ):
        rivalry = (
            CatSiblingRivalrySystem(
                self.cats
            )
        )

        rivalry.compete(
            self.first,
            self.second,
            resource="food",
            intensity=1.0,
        )

        result = rivalry.reconcile(
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
            CatSiblingsReconciledEvent,
        )

        self.assertTrue(
            result.reconciled
        )

        self.assertIsInstance(
            first_event,
            CatSiblingsReconciledEvent,
        )

        self.assertIsInstance(
            second_event,
            CatSiblingsReconciledEvent,
        )

        self.assertEqual(
            first_event,
            result,
        )

        self.assertEqual(
            second_event,
            result,
        )

        self.assertIsNot(
            first_event,
            result,
        )

        self.assertIsNot(
            second_event,
            result,
        )

        self.assertIsNot(
            first_event,
            second_event,
        )

        self.assert_object_only(
            result
        )

    def test_parental_teaching_returns_and_stores_objects(
        self
    ):
        teaching = (
            CatParentalTeachingSystem(
                self.cats
            )
        )

        result = teaching.teach(
            self.mother,
            self.first,
            skill="socialization",
            progress=0.4,
            current_day=20,
        )

        parent_event = (
            self.mother.social_interactions[
                -1
            ]
        )

        kitten_event = (
            self.first.social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatParentTaughtKittenEvent,
        )

        self.assertTrue(
            result.taught
        )

        self.assertEqual(
            result.parent_role,
            "mother",
        )

        for event in (
            parent_event,
            kitten_event,
        ):
            self.assertIsInstance(
                event,
                CatParentTaughtKittenEvent,
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
            parent_event,
            kitten_event,
        )

    def test_parental_teaching_denial_is_object(
        self
    ):
        stranger = self.cats.create_cat(
            name="object_teacher_stranger",
            color="gray",
            fur_length="short",
        )

        result = CatParentalTeachingSystem(
            self.cats
        ).teach(
            stranger,
            self.first,
            skill="socialization",
        )

        self.assertIsInstance(
            result,
            CatParentalTeachingDeniedResult,
        )

        self.assertFalse(
            result.taught
        )

        self.assertEqual(
            result.reason,
            "not_parent",
        )

        self.assert_object_only(
            result
        )

    def test_human_interaction_returns_and_stores_object(
        self
    ):
        human = Human(
            "object_human"
        )

        bonds = CatHumanBondSystem(
            self.cats
        )

        result = bonds.remember_interaction(
            self.first,
            human,
            positive=True,
            significance=0.2,
        )

        stored = (
            self.first.social_interactions[
                -1
            ]
        )

        self.assertIsInstance(
            result,
            CatHumanInteractionRememberedEvent,
        )

        self.assertIsInstance(
            stored,
            CatHumanInteractionRememberedEvent,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            stored
        )

    def test_human_bond_evaluation_is_object_and_meow_consumer_uses_it(
        self
    ):
        human = Human(
            "right_human"
        )

        bonds = CatHumanBondSystem(
            self.cats
        )

        unknown = bonds.evaluate(
            self.first,
            human,
        )

        self.assertIsInstance(
            unknown,
            CatHumanBondEvaluationResult,
        )

        self.assertFalse(
            unknown.right_human
        )

        self.assertEqual(
            unknown.reason,
            "human_not_known",
        )

        for _ in range(8):
            bonds.remember_interaction(
                self.first,
                human,
                positive=True,
                significance=0.15,
            )

        result = bonds.evaluate(
            self.first,
            human,
        )

        self.assertIsInstance(
            result,
            CatHumanBondEvaluationResult,
        )

        self.assertTrue(
            result.right_human
        )

        self.assertGreater(
            result.score,
            0.0,
        )

        invitation = (
            CatMeowInvitationSystem(
                self.cats
            ).offer(
                self.first,
                human,
            )
        )

        self.assertTrue(
            invitation.offered
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
