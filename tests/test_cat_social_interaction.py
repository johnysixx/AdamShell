import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat import Cat
from cats.development_resolver import (
    CatDevelopmentResolver
)


class CatSocialInteractionTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

    def test_created_cat_is_real_cat_object(
        self
    ):
        cat = self.cats.create_cat(
            name="social_cat",
            color="orange",
            fur_length="short"
        )

        self.assertIsInstance(
            cat,
            Cat
        )

        self.assertEqual(
            cat.name,
            "social_cat"
        )

    def test_cat_can_accept_pet(
        self
    ):
        cat = self.cats.create_cat(
            name="pet_cat",
            color="orange",
            fur_length="short"
        )

        human = {
            "name": "human_1",
            "type": "human"
        }

        result = cat.accept_pet(
            human
        )

        self.assertTrue(
            result["accepted"]
        )

        self.assertEqual(
            result["cat"],
            "pet_cat"
        )

        self.assertEqual(
            result["by"],
            "human_1"
        )

        self.assertEqual(
            cat.pet_count,
            1
        )

        self.assertIn(
            result,
            cat.social_interactions
        )

    def test_manifested_cat_can_meow_to_entity(
        self
    ):
        cat = self.cats.create_cat(
            name="talking_cat",
            color="black",
            fur_length="short",
            origin="dice_manifestation"
        )

        listener = {
            "name": "listener_1",
            "type": "idea_entity"
        }

        result = cat.meow_to(
            listener
        )

        self.assertTrue(
            result["spoken"]
        )

        self.assertEqual(
            result["listener"],
            "listener_1"
        )

        self.assertIn(
            "bar_knowledge",
            result["contains"]
        )

        self.assertEqual(
            cat.meow_count,
            1
        )

    def test_cat_can_meow_specific_known_topic(
        self
    ):
        cat = self.cats.create_cat(
            name="bar_cat",
            color="orange",
            fur_length="short"
        )

        listener = {
            "name": "listener_2"
        }

        result = cat.meow_to(
            listener,
            topic="bar_knowledge"
        )

        self.assertTrue(
            result["spoken"]
        )

        self.assertEqual(
            result["contains"],
            [
                "bar_knowledge"
            ]
        )

    def test_cat_refuses_unknown_meow_topic(
        self
    ):
        cat = self.cats.create_cat(
            name="honest_cat",
            color="white",
            fur_length="short"
        )

        result = cat.meow_to(
            {
                "name": "listener_3"
            },
            topic="knowledge_of_everything"
        )

        self.assertFalse(
            result["spoken"]
        )

        self.assertEqual(
            result["reason"],
            "unknown_meow_topic"
        )

    def test_newborn_cannot_use_adult_meow_before_learning(
        self
    ):
        kitten = self.cats.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        kitten["mother_name"] = "mother"

        development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        development.initialize_newborn(
            kitten,
            birth_day=0
        )

        result = kitten.meow_to(
            {
                "name": "listener_4"
            }
        )

        self.assertFalse(
            result["spoken"]
        )

        self.assertEqual(
            result["reason"],
            "meow_not_learned"
        )


if __name__ == "__main__":
    unittest.main()
