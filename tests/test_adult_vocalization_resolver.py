import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.cat_learning import CatLearning
from cats.adult_vocalization_resolver import (
    AdultVocalizationResolver
)
from cats.meow_knowledge_resolver import (
    MeowKnowledgeResolver
)


class AdultVocalizationResolverTests(
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

        self.vocalization = (
            AdultVocalizationResolver(
                self.universe
            )
        )

        self.meow = MeowKnowledgeResolver(
            self.universe
        )

        self.mother = self.cats.create_cat(
            name="mother",
            color="black",
            fur_length="short",
            origin="natural_birth"
        )

        self.kitten = self.cats.create_cat(
            name="kitten",
            color="white",
            fur_length="short",
            origin="kitten_birth_resolver"
        )

        self.kitten["mother_name"] = "mother"

        self.development.initialize_newborn(
            self.kitten,
            birth_day=0
        )

    def test_newborn_knows_no_adult_vocalizations(self):
        vocalizations = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "adult_meowing"
        ][
            "vocalizations"
        ]

        self.assertEqual(
            set(vocalizations.keys()),
            set(
                CatLearning.ADULT_VOCALIZATIONS
            )
        )

        self.assertFalse(
            any(
                vocalizations.values()
            )
        )

    def test_mother_teaches_one_vocalization(self):
        result = self.vocalization.teach(
            teacher=self.mother,
            kitten=self.kitten,
            vocalization="food_request",
            current_day=60
        )

        self.assertTrue(
            result["taught"]
        )

        self.assertTrue(
            self.kitten[
                "learning"
            ][
                "skills"
            ][
                "adult_meowing"
            ][
                "vocalizations"
            ][
                "food_request"
            ]
        )

        self.assertFalse(
            self.kitten[
                "learning"
            ][
                "adult_meowing_learned"
            ]
        )

    def test_complete_repertoire_is_learned(self):
        result = self.vocalization.teach_all(
            teacher=self.mother,
            kitten=self.kitten,
            current_day=70
        )

        skill = self.kitten[
            "learning"
        ][
            "skills"
        ][
            "adult_meowing"
        ]

        self.assertTrue(
            result["complete"]
        )

        self.assertTrue(
            skill["learned"]
        )

        self.assertTrue(
            all(
                skill[
                    "vocalizations"
                ].values()
            )
        )

        self.assertTrue(
            self.kitten[
                "learning"
            ][
                "adult_meowing_learned"
            ]
        )

    def test_meow_is_denied_without_adult_repertoire(self):
        for skill_name in (
            "socialization",
            "litter_box",
            "box_travel",
            "cat_door_travel",
            "hunting",
            "human_communication"
        ):
            skill = self.kitten[
                "learning"
            ][
                "skills"
            ][
                skill_name
            ]

            skill.update({
                "learned": True,
                "progress": 1.0,
                "teacher": "mother",
                "learned_on_day": 70
            })

        self.kitten[
            "learning"
        ][
            "human_communication_learned"
        ] = True

        result = self.meow.transmit(
            mother=self.mother,
            kitten=self.kitten,
            current_day=75
        )

        self.assertFalse(
            result["transmitted"]
        )

        self.assertIn(
            "adult_meowing",
            result[
                "missing_experiences"
            ]
        )

    def test_meow_remains_separate_from_vocalizations(self):
        self.vocalization.teach_all(
            teacher=self.mother,
            kitten=self.kitten,
            current_day=70
        )

        self.assertTrue(
            self.kitten[
                "learning"
            ][
                "skills"
            ][
                "adult_meowing"
            ][
                "learned"
            ]
        )

        self.assertFalse(
            self.kitten[
                "learning"
            ][
                "meow_knowledge"
            ][
                "learned"
            ]
        )


if __name__ == "__main__":
    unittest.main()