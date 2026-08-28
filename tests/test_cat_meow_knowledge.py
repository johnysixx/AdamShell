import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.cat_learning import CatLearning


class CatMeowKnowledgeTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.development = (
            CatDevelopmentResolver(
                self.universe
            )
        )

    def test_meow_contains_all_cat_knowledge(self):
        cat = self.cats.create_cat(
            name="manifested_cat",
            color="black",
            fur_length="short",
            origin="dice_manifestation"
        )

        meow = cat.learning[
            "meow_knowledge"
        ]

        self.assertEqual(
            tuple(meow["contains"]),
            CatLearning.MEOW_CONTENTS
        )

        self.assertIn(
            "bar_knowledge",
            meow["contains"]
        )

        self.assertIn(
            "box_knowledge",
            meow["contains"]
        )

        self.assertIn(
            "cat_door_knowledge",
            meow["contains"]
        )

        self.assertIn(
            "cronenberg_hunting",
            meow["contains"]
        )

    def test_manifested_cat_already_knows_meow(self):
        cat = self.cats.create_cat(
            name="dice_cat",
            color="black",
            fur_length="short",
            origin="dice_manifestation"
        )

        meow = cat.learning[
            "meow_knowledge"
        ]

        self.assertTrue(
            meow["learned"]
        )

        self.assertTrue(
            meow["understood"]
        )

        self.assertTrue(
            meow["can_speak"]
        )

        self.assertEqual(
            meow["source"],
            "manifestation"
        )

    def test_newborn_does_not_yet_know_meow(self):
        kitten = self.cats.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        kitten["mother_name"] = "mother"

        self.development.initialize_newborn(
            kitten,
            birth_day=0
        )

        meow = kitten["learning"][
            "meow_knowledge"
        ]

        self.assertFalse(
            meow["learned"]
        )

        self.assertFalse(
            meow["understood"]
        )

        self.assertFalse(
            meow["can_speak"]
        )

        self.assertIsNone(
            meow["teacher"]
        )

        self.assertIsNone(
            meow["source"]
        )

    def test_meow_schema_is_shared_by_every_cat(self):
        manifested = self.cats.create_cat(
            name="manifested",
            color="black",
            fur_length="short",
            origin="dice_manifestation"
        )

        newborn = self.cats.create_cat(
            name="newborn",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        newborn["mother_name"] = "mother"

        self.development.initialize_newborn(
            newborn,
            birth_day=0
        )

        manifested_schema = set(
            manifested["learning"][
                "meow_knowledge"
            ].keys()
        )

        newborn_schema = set(
            newborn["learning"][
                "meow_knowledge"
            ].keys()
        )

        self.assertEqual(
            manifested_schema,
            newborn_schema
        )


if __name__ == "__main__":
    unittest.main()