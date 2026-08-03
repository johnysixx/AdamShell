import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.feline_wisdom import (
    FelineWisdom
)
from cats.feline_ability_resolver import (
    FelineAbilityResolver
)


class FelineAbilityLearningTests(
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

        self.pazuzu = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short",
            origin="canonical_birth"
        )

        self.queen = self.cats.create_cat(
            name="queen_elisabeth",
            color="calico",
            pattern="tricolor",
            eye_color="green",
            fur_length="long",
            origin="canonical_birth"
        )

        self.dice_teacher = (
            self.cats.create_cat(
                name="dice_teacher",
                color="gray",
                fur_length="short",
                origin="dice_manifestation"
            )
        )

        self.kitten = self.cats.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        FelineWisdom.ensure_state(
            self.dice_teacher,
            can_transmit_meow=True
        )

        self.resolver.register_pazuzu_door_method(
            self.pazuzu
        )

        self.resolver.register_queen_elisabeth_door_method(
            self.queen
        )

    def test_meow_transfers_awareness_not_method(self):
        FelineWisdom.add_awareness(
            cat=self.dice_teacher,
            knowledge_name=(
                "open_human_door"
            ),
            domain="feline",
            description=(
                "Some cats can open unlocked "
                "human doors."
            ),
            known_teachers=[
                "pazuzu",
                "queen_elisabeth"
            ]
        )

        result = (
            self.resolver
            .transmit_meow_awareness(
                teacher=self.dice_teacher,
                student=self.kitten
            )
        )

        wisdom = self.kitten[
            "feline_wisdom"
        ]

        self.assertTrue(
            result["transmitted"]
        )

        self.assertEqual(
            result["methods_transferred"],
            0
        )

        self.assertTrue(
            wisdom[
                "awareness"
            ][
                "open_human_door"
            ][
                "known_to_exist"
            ]
        )

        self.assertNotIn(
            "open_human_door",
            wisdom["abilities"]
        )

    def test_pazuzu_teaches_handle_method(self):
        result = self.resolver.teach_method(
            teacher=self.pazuzu,
            student=self.kitten,
            ability_name="open_human_door",
            method_name="hang_on_handle"
        )

        self.assertTrue(
            result["learned"]
        )

        toward = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=False,
                opens_toward_cat=True
            )
        )

        away = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=False,
                opens_toward_cat=False
            )
        )

        self.assertTrue(
            toward["allowed"]
        )

        self.assertTrue(
            away["allowed"]
        )

    def test_queen_teaches_only_pull_direction(self):
        self.resolver.teach_method(
            teacher=self.queen,
            student=self.kitten,
            ability_name="open_human_door",
            method_name="pull_with_paw"
        )

        toward = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=False,
                opens_toward_cat=True
            )
        )

        away = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=False,
                opens_toward_cat=False
            )
        )

        self.assertTrue(
            toward["allowed"]
        )

        self.assertFalse(
            away["allowed"]
        )

        self.assertEqual(
            away["reason"],
            (
                "no_learned_method_for_"
                "door_direction"
            )
        )

    def test_locked_door_cannot_be_opened(self):
        self.resolver.teach_method(
            teacher=self.pazuzu,
            student=self.kitten,
            ability_name="open_human_door",
            method_name="hang_on_handle"
        )

        result = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=True,
                opens_toward_cat=True
            )
        )

        self.assertFalse(
            result["allowed"]
        )

        self.assertEqual(
            result["reason"],
            "door_is_locked"
        )

    def test_no_cat_can_close_human_door(self):
        pazuzu_result = (
            self.resolver
            .can_close_human_door(
                self.pazuzu
            )
        )

        queen_result = (
            self.resolver
            .can_close_human_door(
                self.queen
            )
        )

        self.assertFalse(
            pazuzu_result["allowed"]
        )

        self.assertFalse(
            queen_result["allowed"]
        )

    def test_cat_can_learn_both_methods(self):
        self.resolver.teach_method(
            teacher=self.pazuzu,
            student=self.kitten,
            ability_name="open_human_door",
            method_name="hang_on_handle"
        )

        self.resolver.teach_method(
            teacher=self.queen,
            student=self.kitten,
            ability_name="open_human_door",
            method_name="pull_with_paw"
        )

        methods = self.kitten[
            "feline_wisdom"
        ][
            "abilities"
        ][
            "open_human_door"
        ][
            "methods"
        ]

        self.assertEqual(
            set(methods),
            {
                "hang_on_handle",
                "pull_with_paw"
            }
        )



    def test_queen_cannot_open_locked_door(self):
        self.resolver.teach_method(
            teacher=self.queen,
            student=self.kitten,
            ability_name="open_human_door",
            method_name="pull_with_paw"
        )

        result = (
            self.resolver
            .can_open_human_door(
                cat=self.kitten,
                locked=True,
                opens_toward_cat=True
            )
        )

        self.assertFalse(
            result["allowed"]
        )

        self.assertEqual(
            result["reason"],
            "door_is_locked"
        )


if __name__ == "__main__":
    unittest.main()