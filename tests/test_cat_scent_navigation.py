import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import (
    CatKnowledge
)
from cats.cat_mind import (
    CatMind
)


class CatScentNavigationTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="tracker",
            color="black",
            fur_length="short"
        )

        self.cat["current_layer"] = (
            "quantum_layer"
        )

        self.cat["position"] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        CatKnowledge.remember_scent_place(
            cat=self.cat,
            layer="quantum_layer",
            position={
                "x": 5.0,
                "y": 0.0,
                "z": 0.0
            },
            source_id="box_pazuzu",
            recognized_identity=(
                "cat:pazuzu"
            ),
            components={
                "cat": 1.0,
                "fur": 0.8
            },
            perceived_intensity=0.8,
            universe_tick=10
        )

    def observations(self):
        return {
            "bar_known": True,
            "bar_visible": False,
            "visible_cronenbergs": [],
            "huntable_cronenbergs": [],
            "cronenberg_danger": 0.0,
            "unexplored_boxes": [],
            "can_create_exploration_pair": False,
            "nearby_cats": [],
            "shareable_legend_count": 0,
            "cronenberg_scent_recognized": False
        }

    def test_cat_mind_can_choose_known_scent(
        self
    ):
        traits = self.cat[
            "personality"
        ][
            "traits"
        ]

        traits["curiosity"] = 1.0
        traits["courage"] = 0.8

        candidates = CatMind.consider(
            cat=self.cat,
            observations=self.observations()
        )

        scent = [
            candidate
            for candidate in candidates
            if candidate[
                "type"
            ] == "follow_known_scent"
        ]

        self.assertEqual(
            len(scent),
            1
        )

        self.assertEqual(
            scent[0][
                "target"
            ][
                "identity"
            ],
            "cat:pazuzu"
        )

    def test_planner_remembers_strongest_scent_place(
        self
    ):
        from cats.cat_exploration_planner import (
            CatExplorationPlanner
        )

        result = (
            CatExplorationPlanner
            .choose_scent_destination(
                cat=self.cat,
                preferred_identity=(
                    "cat:pazuzu"
                )
            )
        )

        self.assertTrue(
            result["selected"]
        )

        self.assertEqual(
            result["position"],
            {
                "x": 5.0,
                "y": 0.0,
                "z": 0.0
            }
        )


if __name__ == "__main__":
    unittest.main()