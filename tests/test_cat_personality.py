import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_personality import (
    CatPersonality
)


class CatPersonalityTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="personality_cat",
            color="black",
            fur_length="short"
        )

    def test_new_cat_has_neutral_personality(
        self
    ):
        traits = self.cat[
            "personality"
        ][
            "traits"
        ]

        self.assertEqual(
            set(traits),
            set(
                CatPersonality.TRAITS
            )
        )

        self.assertTrue(
            all(
                value == 0.5
                for value in traits.values()
            )
        )

    def test_trait_can_increase(
        self
    ):
        event = CatPersonality.adjust(
            cat=self.cat,
            trait="courage",
            amount=0.2,
            source="successful_hunt",
            day=10
        )

        self.assertAlmostEqual(
            self.cat[
                "personality"
            ][
                "traits"
            ][
                "courage"
            ],
            0.7
        )

        self.assertAlmostEqual(
            event["applied_change"],
            0.2
        )

    def test_trait_can_decrease(
        self
    ):
        CatPersonality.adjust(
            cat=self.cat,
            trait="patience",
            amount=-0.15,
            source="frustration"
        )

        self.assertAlmostEqual(
            self.cat[
                "personality"
            ][
                "traits"
            ][
                "patience"
            ],
            0.35
        )

    def test_traits_are_clamped_to_valid_range(
        self
    ):
        CatPersonality.adjust(
            cat=self.cat,
            trait="aggression",
            amount=10.0,
            source="extreme_test"
        )

        self.assertEqual(
            self.cat[
                "personality"
            ][
                "traits"
            ][
                "aggression"
            ],
            1.0
        )

        CatPersonality.adjust(
            cat=self.cat,
            trait="aggression",
            amount=-20.0,
            source="extreme_test"
        )

        self.assertEqual(
            self.cat[
                "personality"
            ][
                "traits"
            ][
                "aggression"
            ],
            0.0
        )

    def test_experience_changes_multiple_traits(
        self
    ):
        result = (
            CatPersonality
            .apply_experience(
                cat=self.cat,
                source="successful_cronenberg_hunt",
                changes={
                    "courage": 0.05,
                    "aggression": 0.03,
                    "curiosity": 0.01
                },
                day=20
            )
        )

        self.assertTrue(
            result["applied"]
        )

        traits = self.cat[
            "personality"
        ][
            "traits"
        ]

        self.assertAlmostEqual(
            traits["courage"],
            0.55
        )

        self.assertAlmostEqual(
            traits["aggression"],
            0.53
        )

        self.assertAlmostEqual(
            traits["curiosity"],
            0.51
        )

    def test_personality_history_is_preserved(
        self
    ):
        CatPersonality.adjust(
            cat=self.cat,
            trait="empathy",
            amount=0.1,
            source="helped_kitten"
        )

        personality = self.cat[
            "personality"
        ]

        self.assertEqual(
            personality[
                "experiences_processed"
            ],
            1
        )

        self.assertEqual(
            len(
                personality["history"]
            ),
            1
        )

    def test_dominant_trait_is_returned(
        self
    ):
        CatPersonality.adjust(
            cat=self.cat,
            trait="curiosity",
            amount=0.4,
            source="exploration"
        )

        self.assertEqual(
            CatPersonality.dominant_trait(
                self.cat
            ),
            "curiosity"
        )


if __name__ == "__main__":
    unittest.main()