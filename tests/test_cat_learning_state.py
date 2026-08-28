import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)


class CatLearningStateTests(
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

    def test_every_cat_has_same_learning_schema(self):
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

        self.assertEqual(
            set(
                manifested["learning"].keys()
            ),
            set(
                newborn["learning"].keys()
            )
        )

        self.assertEqual(
            set(
                manifested["learning"][
                    "skills"
                ].keys()
            ),
            set(
                newborn["learning"][
                    "skills"
                ].keys()
            )
        )

    def test_manifested_cat_already_knows_cat_skills(self):
        cat = self.cats.create_cat(
            name="dice_cat",
            color="black",
            fur_length="short",
            origin="dice_manifestation"
        )

        self.assertTrue(
            cat.learning["complete"]
        )

        self.assertFalse(
            cat.learning[
                "teaching_required"
            ]
        )

        self.assertTrue(
            all(
                skill["learned"]
                for skill
                in cat.learning[
                    "skills"
                ].values()
            )
        )

    def test_newborn_requires_maternal_teaching(self):
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

        learning = kitten["learning"]

        self.assertTrue(
            learning["teaching_required"]
        )

        self.assertEqual(
            learning[
                "teaching_deadline_days"
            ],
            90
        )

        self.assertEqual(
            learning["teacher_mother"],
            "mother"
        )

        self.assertTrue(
            learning[
                "kitten_meowing_instinctive"
            ]
        )

        self.assertFalse(
            learning[
                "adult_meowing_learned"
            ]
        )

        self.assertFalse(
            learning[
                "human_communication_learned"
            ]
        )

        self.assertFalse(
            learning["complete"]
        )


if __name__ == "__main__":
    unittest.main()