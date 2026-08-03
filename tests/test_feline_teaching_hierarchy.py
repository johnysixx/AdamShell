import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.feline_wisdom import (
    FelineWisdom
)
from cats.feline_ability_resolver import (
    FelineAbilityResolver
)


class FelineTeachingHierarchyTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.resolver = (
            FelineAbilityResolver(
                self.universe
            )
        )

        self.garfield = self.cats.create_cat(
            name="garfield",
            color="orange",
            fur_length="short",
            origin="canonical_birth"
        )

        self.pazuzu = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short",
            origin="canonical_birth"
        )

        self.foreign_cat = self.cats.create_cat(
            name="foreign_cat",
            color="gray",
            fur_length="short",
            origin="natural_birth"
        )

        self.kitten = self.cats.create_cat(
            name="kitten",
            color="black",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        self.kitten["parents"] = {
            "mother": None,
            "father": "pazuzu"
        }

        self.resolver.register_garfield_teaching_abilities(
            self.garfield
        )

        self.resolver.register_pazuzu_door_method(
            self.pazuzu
        )

    def teach_pazuzu_to_teach(self):
        return self.resolver.teach_method(
            teacher=self.garfield,
            student=self.pazuzu,
            ability_name="teach_other_cats",
            method_name="garfield_teaching_method"
        )

    def teach_pazuzu_meta_teaching(self):
        return self.resolver.teach_method(
            teacher=self.garfield,
            student=self.pazuzu,
            ability_name="teach_teaching",
            method_name=(
                "garfield_meta_teaching_method"
            )
        )

    def test_garfield_can_teach_any_cat_to_teach(self):
        result = self.teach_pazuzu_to_teach()

        self.assertTrue(
            result["learned"]
        )

        ability = self.pazuzu[
            "feline_wisdom"
        ][
            "abilities"
        ][
            "teach_other_cats"
        ]

        self.assertTrue(
            ability["learned"]
        )

    def test_teacher_can_teach_own_ability(self):
        self.teach_pazuzu_to_teach()

        result = self.resolver.teach_method(
            teacher=self.pazuzu,
            student=self.foreign_cat,
            ability_name="open_human_door",
            method_name="hang_on_handle"
        )

        self.assertTrue(
            result["learned"]
        )

    def test_parent_can_pass_teaching_to_own_kitten(self):
        self.teach_pazuzu_to_teach()

        result = self.resolver.teach_method(
            teacher=self.pazuzu,
            student=self.kitten,
            ability_name="teach_other_cats",
            method_name="garfield_teaching_method"
        )

        self.assertTrue(
            result["learned"]
        )

        self.assertTrue(
            self.kitten[
                "feline_wisdom"
            ][
                "abilities"
            ][
                "teach_other_cats"
            ][
                "learned"
            ]
        )

    def test_forbidden_foreign_teacher_creation_makes_cronenberg(
        self
    ):
        self.teach_pazuzu_to_teach()

        previous_count = (
            self.universe.cronenberg_count
        )

        result = self.resolver.teach_method(
            teacher=self.pazuzu,
            student=self.foreign_cat,
            ability_name="teach_other_cats",
            method_name="garfield_teaching_method"
        )

        self.assertFalse(
            result["learned"]
        )

        self.assertTrue(
            result["cronenberg_created"]
        )

        self.assertEqual(
            self.universe.cronenberg_count,
            previous_count + 1
        )

        self.assertEqual(
            self.universe.cronenbergs[-1].id,
            result["cronenberg_id"]
        )

        self.assertNotIn(
            "teach_other_cats",
            self.foreign_cat[
                "feline_wisdom"
            ][
                "abilities"
            ]
        )

    def test_meta_teacher_can_create_foreign_teacher(self):
        self.teach_pazuzu_to_teach()
        self.teach_pazuzu_meta_teaching()

        previous_count = (
            self.universe.cronenberg_count
        )

        result = self.resolver.teach_method(
            teacher=self.pazuzu,
            student=self.foreign_cat,
            ability_name="teach_other_cats",
            method_name="garfield_teaching_method"
        )

        self.assertTrue(
            result["learned"]
        )

        self.assertEqual(
            self.universe.cronenberg_count,
            previous_count
        )

    def test_untrained_cat_cannot_teach_foreign_cat(self):
        result = self.resolver.teach_method(
            teacher=self.foreign_cat,
            student=self.pazuzu,
            ability_name="open_human_door",
            method_name="hang_on_handle"
        )

        self.assertFalse(
            result["learned"]
        )

        self.assertEqual(
            result["reason"],
            "teacher_has_not_learned_to_teach"
        )


if __name__ == "__main__":
    unittest.main()