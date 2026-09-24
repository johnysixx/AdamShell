import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_personality import (
    CatPersonality,
)
from cats.cat_personality_state import (
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
            event,
            CatPersonalityTraitAdjustedEvent,
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
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["trait"]

        result["trait"] = "changed"

        result[
            "metadata"
        ][
            "prey"
        ] = "changed"

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

    def test_state_snapshot_serializes_history(
        self
    ):
        CatPersonality.adjust(
            cat=self.cat,
            trait="empathy",
            amount=0.1,
            source="helped_kitten",
        )

        event = (
            self.cat
            .personality
            .history[-1]
        )

        snapshot = (
            self.cat
            .personality
            .to_dict()
        )

        snapshot[
            "history"
        ][0][
            "trait"
        ] = "changed"

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
