import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_social_objects import CatRelationship
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
            self.first.bonds.records[self.second.name].active
        )

        self.assertEqual(
            self.first.bonds.records[self.second.name].source,
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

        first_relation = self.first.relationships[self.second.name]
        second_relation = self.second.relationships[self.first.name]
        self.assertIsInstance(first_relation, CatRelationship)
        self.assertIsInstance(second_relation, CatRelationship)
        self.assertIsNot(first_relation, second_relation)
        self.assertAlmostEqual(first_relation.tension, 0.096)
        self.assertAlmostEqual(second_relation.tension, 0.096)

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
            self.first.learning.teacher_mother,
            self.mother.name
        )
        relation = self.first.relationships[self.mother.name]
        self.assertIsInstance(relation, CatRelationship)
        self.assertAlmostEqual(relation.trust, 0.54)
        self.assertAlmostEqual(relation.familiarity, 0.03)
        self.assertAlmostEqual(relation.affiliation, 0.02)
        self.assertEqual(relation.last_interaction, 'parental_teaching')

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
            self.first.learning.hunting_teacher_father,
            self.father.name
        )
        relation = self.first.relationships[self.father.name]
        self.assertIsInstance(relation, CatRelationship)
        self.assertAlmostEqual(relation.trust, 0.54)
        self.assertEqual(relation.last_interaction, 'parental_teaching')

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
            self.first.learning.skills[
                "litter_box"
            ].learned
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


    def test_rivalry_and_reconciliation_preserve_existing_relationships(self):
        relation = CatRelationship.create()
        relation.trust = 0.8
        relation.tension = 0.4
        relation.affiliation = 0.6
        relation.meet_count = 4
        history = [{'reason': 'past_meeting'}]
        relation.trust_history = history
        legacy = {'trust': 0.7, 'custom_note': 'known_before_rivalry'}
        self.first.relationships[self.second.name] = relation
        self.second.relationships[self.first.name] = legacy

        rivalry = CatSiblingRivalrySystem(self.cats)
        competed = rivalry.compete(
            self.first, self.second, resource='food', intensity=0.5,
        )
        self.assertTrue(competed['competed'])
        self.assertAlmostEqual(relation.tension, 0.46)
        self.assertAlmostEqual(legacy['tension'], 0.06)

        reconciled = rivalry.reconcile(self.first, self.second)
        self.assertTrue(reconciled['reconciled'])
        self.assertIs(self.first.relationships[self.second.name], relation)
        self.assertIs(self.second.relationships[self.first.name], legacy)
        self.assertAlmostEqual(relation.trust, 0.8)
        self.assertAlmostEqual(relation.tension, 0.31)
        self.assertAlmostEqual(relation.affiliation, 0.63)
        self.assertEqual(relation.meet_count, 4)
        self.assertIs(relation.trust_history, history)
        self.assertAlmostEqual(legacy['trust'], 0.7)
        self.assertAlmostEqual(legacy['tension'], 0.0)
        self.assertAlmostEqual(legacy['affiliation'], 0.05)
        self.assertEqual(legacy['custom_note'], 'known_before_rivalry')


    def test_parental_lessons_preserve_existing_relationship_records(self):
        relation = CatRelationship.create()
        relation.trust = 0.8
        relation.familiarity = 0.2
        relation.affiliation = 0.3
        relation.tension = 0.1
        relation.meet_count = 4
        history = [{'reason': 'past_meeting'}]
        relation.trust_history = history
        legacy = {'trust': 0.7, 'custom_note': 'known_before_lessons'}
        self.first.relationships[self.mother.name] = relation
        self.first.relationships[self.father.name] = legacy

        teaching = CatParentalTeachingSystem(self.cats)
        for _ in range(2):
            mother_result = teaching.teach(
                self.mother, self.first, skill='socialization',
            )
            father_result = teaching.teach(
                self.father, self.first, skill='hunting',
            )
            self.assertTrue(mother_result['taught'])
            self.assertTrue(father_result['taught'])

        self.assertIs(self.first.relationships[self.mother.name], relation)
        self.assertIs(self.first.relationships[self.father.name], legacy)
        self.assertAlmostEqual(relation.trust, 0.88)
        self.assertAlmostEqual(relation.familiarity, 0.26)
        self.assertAlmostEqual(relation.affiliation, 0.34)
        self.assertAlmostEqual(relation.tension, 0.1)
        self.assertEqual(relation.meet_count, 4)
        self.assertIs(relation.trust_history, history)
        self.assertEqual(relation.last_interaction, 'parental_teaching')
        self.assertAlmostEqual(legacy['trust'], 0.78)
        self.assertAlmostEqual(legacy['familiarity'], 0.06)
        self.assertAlmostEqual(legacy['affiliation'], 0.04)
        self.assertEqual(legacy['custom_note'], 'known_before_lessons')


if __name__ == "__main__":
    unittest.main()
