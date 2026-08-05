import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_personality import (
    CatPersonality
)


class CatMindTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="thinking_cat",
            color="black",
            fur_length="short"
        )

    def traits(self):
        return self.cat[
            "personality"
        ][
            "traits"
        ]

    def test_new_cat_has_empty_mind(
        self
    ):
        mind = self.cat["mind"]

        self.assertIsNone(
            mind["current_intention"]
        )

        self.assertEqual(
            mind["decision_count"],
            0
        )

        self.assertEqual(
            mind["history"],
            []
        )

    def test_curious_cat_prefers_new_box(
        self
    ):
        self.traits()["curiosity"] = 1.0
        self.traits()["courage"] = 0.7

        result = CatMind.decide(
            cat=self.cat,
            observations={
                "unexplored_boxes": [
                    "box_alpha"
                ]
            }
        )

        self.assertEqual(
            result["intention"],
            "explore_box"
        )

        self.assertEqual(
            result["target"],
            "box_alpha"
        )

    def test_brave_aggressive_cat_considers_hunt(
        self
    ):
        self.traits()["courage"] = 1.0
        self.traits()["aggression"] = 1.0
        self.traits()["curiosity"] = 0.7

        candidates = CatMind.consider(
            cat=self.cat,
            observations={
                "huntable_cronenbergs": [
                    "cronenberg_small"
                ],
                "cronenberg_danger": 0.2
            }
        )

        self.assertEqual(
            candidates[0]["type"],
            "hunt_cronenberg"
        )

    def test_positive_bar_memory_raises_bar_score(
        self
    ):
        before = CatMind.consider(
            cat=self.cat,
            observations={
                "bar_known": True
            }
        )

        before_score = next(
            candidate["score"]
            for candidate in before
            if candidate["type"]
            == "visit_bar"
        )

        self.cat["memory"].remember(
            event_type=(
                "cat_drank_milk_at_bar"
            ),
            location="meeting_place"
        )

        after = CatMind.consider(
            cat=self.cat,
            observations={
                "bar_known": True
            }
        )

        after_score = next(
            candidate["score"]
            for candidate in after
            if candidate["type"]
            == "visit_bar"
        )

        self.assertGreater(
            after_score,
            before_score
        )

    def test_quantum_roll_only_selects_among_finalists(
        self
    ):
        result = CatMind.decide(
            cat=self.cat,
            observations={
                "bar_known": True,
                "bar_visible": True,
                "unexplored_boxes": [
                    "box_alpha"
                ],
                "nearby_cats": [
                    "other_cat"
                ]
            },
            quantum_roll=20,
            top_count=3
        )

        finalist_types = {
            candidate["type"]
            for candidate
            in result["finalists"]
        }

        self.assertIn(
            result["intention"],
            finalist_types
        )

        self.assertEqual(
            len(
                result["finalists"]
            ),
            3
        )

    def test_decision_is_preserved_in_history(
        self
    ):
        result = CatMind.decide(
            cat=self.cat,
            observations={
                "bar_known": True
            }
        )

        mind = self.cat["mind"]

        self.assertEqual(
            mind["decision_count"],
            1
        )

        self.assertEqual(
            len(
                mind["history"]
            ),
            1
        )

        self.assertEqual(
            mind[
                "current_intention"
            ][
                "type"
            ],
            result["intention"]
        )

    def test_personality_changes_future_decision(
        self
    ):
        observations = {
            "huntable_cronenbergs": [
                "cronenberg_small"
            ],
            "cronenberg_danger": 0.5,
            "unexplored_boxes": [
                "box_alpha"
            ]
        }

        first = CatMind.decide(
            cat=self.cat,
            observations=observations
        )

        CatPersonality.adjust(
            cat=self.cat,
            trait="curiosity",
            amount=0.5,
            source="many_explorations"
        )

        CatPersonality.adjust(
            cat=self.cat,
            trait="courage",
            amount=-0.4,
            source="dangerous_encounter"
        )

        second = CatMind.decide(
            cat=self.cat,
            observations=observations
        )

        self.assertNotEqual(
            first["score"],
            second["score"]
        )


if __name__ == "__main__":
    unittest.main()