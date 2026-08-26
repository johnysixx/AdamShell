import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_family_system import (
    CatFamilySystem
)
from cats.cat_family_bonding_system import (
    CatFamilyBondingSystem
)
from cats.cat_sibling_play_system import (
    CatSiblingPlaySystem
)
from cats.cat_sibling_rivalry_system import (
    CatSiblingRivalrySystem
)
from cats.cat_parental_teaching_system import (
    CatParentalTeachingSystem
)


class CatFamilyBehaviorTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.mother = self.cats.create_cat(
            name="mother",
            color="black",
            fur_length="short"
        )

        self.mother.sex = "female"

        self.father = self.cats.create_cat(
            name="father",
            color="orange",
            fur_length="short"
        )

        self.father.sex = "male"

        self.first = self.cats.create_cat(
            name="kitten_1",
            color="black",
            fur_length="short"
        )

        self.second = self.cats.create_cat(
            name="kitten_2",
            color="black",
            fur_length="short"
        )

        for kitten in (
            self.first,
            self.second
        ):
            kitten.mother_name = (
                self.mother.name
            )

            kitten.father_name = (
                self.father.name
            )

        family = CatFamilySystem(
            self.cats
        )

        family.register_birth(
            mother=self.mother,
            kittens=[
                self.first,
                self.second
            ],
            cats=self.cats.cats
        )

    def test_repeated_sibling_play_can_create_family_bond(
        self
    ):
        play = CatSiblingPlaySystem(
            self.cats
        )

        for _ in range(3):
            play.play(
                self.first,
                self.second,
                age_days=30
            )

        bonding = CatFamilyBondingSystem(
            self.cats
        )

        result = bonding.form_bond(
            self.first,
            self.second
        )

        self.assertTrue(
            result["formed"]
        )

        self.assertTrue(
            self.first.bonds[
                self.second.name
            ]["active"]
        )

        self.assertEqual(
            self.first.bonds[
                self.second.name
            ]["source"],
            "family"
        )

    def test_sibling_rivalry_increases_tension(
        self
    ):
        rivalry = CatSiblingRivalrySystem(
            self.cats
        )

        result = rivalry.compete(
            self.first,
            self.second,
            resource="milk_bowl",
            intensity=0.8
        )

        self.assertTrue(
            result["competed"]
        )

        self.assertGreater(
            self.first.relationships[
                self.second.name
            ]["tension"],
            0.0
        )

    def test_bond_reduces_rivalry_tension_gain(
        self
    ):
        play = CatSiblingPlaySystem(
            self.cats
        )

        for _ in range(3):
            play.play(
                self.first,
                self.second,
                age_days=30
            )

        bonding = CatFamilyBondingSystem(
            self.cats
        )

        bonding.form_bond(
            self.first,
            self.second
        )

        rivalry = CatSiblingRivalrySystem(
            self.cats
        )

        before = (
            self.first.relationships[
                self.second.name
            ]["tension"]
        )

        rivalry.compete(
            self.first,
            self.second,
            resource="window",
            intensity=1.0
        )

        increase = (
            self.first.relationships[
                self.second.name
            ]["tension"]
            - before
        )

        self.assertLessEqual(
            increase,
            0.061
        )

    def test_siblings_can_reconcile(
        self
    ):
        rivalry = CatSiblingRivalrySystem(
            self.cats
        )

        rivalry.compete(
            self.first,
            self.second,
            resource="food",
            intensity=1.0
        )

        before = (
            self.first.relationships[
                self.second.name
            ]["tension"]
        )

        result = rivalry.reconcile(
            self.first,
            self.second
        )

        self.assertTrue(
            result["reconciled"]
        )

        self.assertLess(
            self.first.relationships[
                self.second.name
            ]["tension"],
            before
        )

    def test_mother_can_teach_kitten(
        self
    ):
        teaching = CatParentalTeachingSystem(
            self.cats
        )

        result = teaching.teach(
            self.mother,
            self.first,
            skill="socialization",
            progress=0.4,
            current_day=20
        )

        self.assertTrue(
            result["taught"]
        )

        self.assertEqual(
            result["parent_role"],
            "mother"
        )

        self.assertEqual(
            self.first.learning[
                "teacher_mother"
            ],
            self.mother.name
        )

    def test_father_can_teach_hunting(
        self
    ):
        teaching = CatParentalTeachingSystem(
            self.cats
        )

        result = teaching.teach(
            self.father,
            self.first,
            skill="hunting",
            progress=0.5,
            current_day=50
        )

        self.assertTrue(
            result["taught"]
        )

        self.assertEqual(
            self.first.learning[
                "hunting_teacher_father"
            ],
            self.father.name
        )

    def test_repeated_lessons_can_complete_skill(
        self
    ):
        teaching = CatParentalTeachingSystem(
            self.cats
        )

        for _ in range(4):
            teaching.teach(
                self.mother,
                self.first,
                skill="litter_box",
                progress=0.25
            )

        self.assertTrue(
            self.first.learning[
                "skills"
            ][
                "litter_box"
            ][
                "learned"
            ]
        )

    def test_stranger_cannot_use_parental_teaching(
        self
    ):
        stranger = self.cats.create_cat(
            name="stranger",
            color="gray",
            fur_length="short"
        )

        teaching = CatParentalTeachingSystem(
            self.cats
        )

        result = teaching.teach(
            stranger,
            self.first,
            skill="socialization"
        )

        self.assertFalse(
            result["taught"]
        )

        self.assertEqual(
            result["reason"],
            "not_parent"
        )


if __name__ == "__main__":
    unittest.main()
