import unittest

from universe.universe import Universe
from cats import Cats
from cats.development_resolver import (
    CatDevelopmentResolver
)
from cats.reproduction import (
    CatReproduction
)


class CatDevelopmentResolverTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.cats = Cats(
            self.universe
        )

        self.kitten = self.cats.create_cat(
            name="kitten",
            color="black",
            fur_length="short",
            sex="female"
        )

        self.resolver = (
            CatDevelopmentResolver(
                self.universe
            )
        )

        self.resolver.initialize_newborn(
            self.kitten,
            birth_day=10
        )

    def test_newborn_is_not_fertile(self):
        reproduction = self.kitten[
            "reproduction"
        ]

        self.assertEqual(
            self.kitten["age_days"],
            0
        )

        self.assertEqual(
            self.kitten[
                "developmental_stage"
            ],
            "newborn"
        )

        self.assertFalse(
            reproduction["fertile"]
        )

        self.assertFalse(
            reproduction[
                "reproductive_maturity"
            ]
        )

    def test_developmental_stages_follow_age(self):
        expected = {
            0: "newborn",
            13: "newborn",
            14: "socializing_kitten",
            48: "socializing_kitten",
            49: "playful_kitten",
            97: "playful_kitten",
            98: "juvenile",
            179: "juvenile",
            180: "adolescent",
            364: "adolescent",
            365: "adult"
        }

        for age, stage in expected.items():
            with self.subTest(
                age=age
            ):
                self.assertEqual(
                    self.resolver.stage_for_age(
                        age
                    ),
                    stage
                )

    def test_intact_cat_becomes_fertile_at_six_months(self):
        before = self.resolver.advance_age(
            self.kitten,
            days=179
        )

        self.assertFalse(
            before["fertile"]
        )

        maturity = (
            self.resolver.advance_age(
                self.kitten,
                days=1
            )
        )

        self.assertEqual(
            maturity["age_days"],
            180
        )

        self.assertEqual(
            maturity["stage"],
            "adolescent"
        )

        self.assertTrue(
            maturity[
                "reproductive_maturity"
            ]
        )

        self.assertTrue(
            maturity["fertile"]
        )

    def test_neutered_cat_never_becomes_fertile(self):
        self.kitten[
            "reproduction"
        ] = (
            CatReproduction.create_state(
                sex="female",
                neutered=True
            )
        )

        self.kitten["age_days"] = 0
        self.kitten[
            "developmental_stage"
        ] = "newborn"

        result = self.resolver.advance_age(
            self.kitten,
            days=365
        )

        reproduction = self.kitten[
            "reproduction"
        ]

        self.assertEqual(
            result["stage"],
            "adult"
        )

        self.assertTrue(
            reproduction[
                "reproductive_maturity"
            ]
        )

        self.assertFalse(
            reproduction["fertile"]
        )

    def test_large_age_jump_records_all_transitions(self):
        result = self.resolver.advance_age(
            self.kitten,
            days=365
        )

        self.assertEqual(
            result["transitions"],
            [
                {
                    "day": 14,
                    "stage": (
                        "socializing_kitten"
                    )
                },
                {
                    "day": 49,
                    "stage": (
                        "playful_kitten"
                    )
                },
                {
                    "day": 98,
                    "stage": "juvenile"
                },
                {
                    "day": 180,
                    "stage": "adolescent"
                },
                {
                    "day": 365,
                    "stage": "adult"
                }
            ]
        )


if __name__ == "__main__":
    unittest.main()