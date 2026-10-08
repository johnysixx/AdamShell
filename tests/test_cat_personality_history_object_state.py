import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_personality import (
    CatPersonality,
)
from cats.cat_personality_state import (
    CatPersonalityExperienceAppliedResult,
    CatPersonalityTraitAdjustedEvent,
)


class CatPersonalityHistoryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="personality_history_cat",
            color="black",
            fur_length="short",
        )

    def test_history_uses_object_state(
        self
    ):
        result = CatPersonality.adjust(
            cat=self.cat,
            trait="courage",
            amount=0.2,
            source="successful_hunt",
            day=10,
            metadata={
                "prey": "cronenberg",
            },
        )

        event = (
            self.cat
            .personality
            .history[-1]
        )

        self.assertIsInstance(
            result,
            CatPersonalityTraitAdjustedEvent,
        )

        self.assertIs(
            result,
            event,
        )

        self.assertEqual(
            event.trait,
            "courage",
        )

        self.assertEqual(
            event.source,
            "successful_hunt",
        )

        self.assertEqual(
            event.metadata["prey"],
            "cronenberg",
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["trait"]

        self.assertEqual(
            event.trait,
            "courage",
        )

        self.assertEqual(
            event.metadata["prey"],
            "cronenberg",
        )

        with self.assertRaises(
            TypeError
        ):
            event.metadata[
                "prey"
            ] = "changed"

    def test_experience_result_uses_object_state(
        self
    ):
        result = (
            CatPersonality.apply_experience(
                cat=self.cat,
                source="socialization",
                changes={
                    "empathy": 0.1,
                    "patience": 0.05,
                },
                day=12,
            )
        )

        self.assertIsInstance(
            result,
            CatPersonalityExperienceAppliedResult,
        )

        self.assertTrue(
            result.applied
        )

        self.assertEqual(
            tuple(
                result.changes.keys()
            ),
            (
                "empathy",
                "patience",
            ),
        )

        self.assertEqual(
            len(result.events),
            2,
        )

        self.assertIs(
            result.events[0],
            self.cat.personality.history[-2],
        )

        self.assertIs(
            result.events[1],
            self.cat.personality.history[-1],
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "applied"
            ]

        self.assertEqual(
            result.changes[
                "empathy"
            ],
            0.1,
        )

        self.assertEqual(
            result.events[0].trait,
            "empathy",
        )

    def test_state_has_no_serialization_shim(
        self
    ):
        CatPersonality.adjust(
            cat=self.cat,
            trait="empathy",
            amount=0.1,
            source="helped_kitten",
        )

        state = self.cat.personality
        event = state.history[-1]

        self.assertFalse(
            hasattr(
                state,
                "to_dict",
            )
        )

        self.assertFalse(
            hasattr(
                state.traits,
                "to_dict",
            )
        )

        self.assertFalse(
            hasattr(
                event,
                "to_dict",
            )
        )

        self.assertEqual(
            event.trait,
            "empathy",
        )

    def test_history_rejects_mapping_event(
        self
    ):
        with self.assertRaises(TypeError):
            (
                self.cat
                .personality
                .record_event(
                    {
                        "name": (
                            "cat_personality_"
                            "trait_adjusted"
                        ),
                    }
                )
            )


if __name__ == "__main__":
    unittest.main()
