import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_knowledge import (
    CatKnowledge
)
from cats.cat_exploration_planner import (
    CatExplorationPlanner
)


class CatLegendReputationTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.storyteller = (
            self.cats.create_cat(
                name="pazuzu",
                color="black",
                fur_length="short"
            )
        )

        self.listener = (
            self.cats.create_cat(
                name="garfield",
                color="orange",
                fur_length="short"
            )
        )

        self.listener[
            "relationships"
        ] = {
            "pazuzu": {
                "trust": 0.5
            }
        }

        place = (
            CatKnowledge.remember_place(
                self.storyteller,
                "quantum_layer",
                {
                    "x": 9.0,
                    "y": 1.0,
                    "z": 0.0
                }
            )
        )

        self.legend = (
            CatKnowledge.publish_legend(
                self.universe,
                self.storyteller,
                place
            )
        )

        CatKnowledge.hear_legend(
            self.listener,
            self.storyteller,
            self.legend
        )

    def test_verified_legend_increases_trust(
        self
    ):
        place = (
            CatKnowledge.remember_place(
                self.listener,
                "quantum_layer",
                {
                    "x": 9.0,
                    "y": 1.0,
                    "z": 0.0
                }
            )
        )

        CatKnowledge.verify_heard_legend(
            self.listener,
            place
        )

        trust = (
            self.listener[
                "relationships"
            ][
                "pazuzu"
            ][
                "trust"
            ]
        )

        self.assertAlmostEqual(
            trust,
            0.6
        )

    def test_contradicted_legend_decreases_trust(
        self
    ):
        result = (
            CatKnowledge
            .contradict_heard_legend(
                cat=self.listener,
                legend_id=self.legend[
                    "legend_id"
                ]
            )
        )

        self.assertTrue(
            result["contradicted"]
        )

        trust = (
            self.listener[
                "relationships"
            ][
                "pazuzu"
            ][
                "trust"
            ]
        )

        self.assertAlmostEqual(
            trust,
            0.35
        )

    def test_trust_history_is_recorded(
        self
    ):
        CatKnowledge.contradict_heard_legend(
            self.listener,
            self.legend[
                "legend_id"
            ]
        )

        history = (
            self.listener[
                "relationships"
            ][
                "pazuzu"
            ][
                "trust_history"
            ]
        )

        self.assertEqual(
            len(history),
            1
        )

        self.assertEqual(
            history[0]["reason"],
            (
                "personal_observation_"
                "contradicted"
            )
        )

    def test_trust_is_clamped_to_zero_and_one(
        self
    ):
        for _ in range(20):
            CatKnowledge.adjust_storyteller_trust(
                self.listener,
                "pazuzu",
                0.10,
                "test"
            )

        self.assertEqual(
            self.listener[
                "relationships"
            ][
                "pazuzu"
            ][
                "trust"
            ],
            1.0
        )

        for _ in range(20):
            CatKnowledge.adjust_storyteller_trust(
                self.listener,
                "pazuzu",
                -0.15,
                "test"
            )

        self.assertEqual(
            self.listener[
                "relationships"
            ][
                "pazuzu"
            ][
                "trust"
            ],
            0.0
        )

    def test_contradicted_legend_is_not_used_for_planning(
        self
    ):
        CatKnowledge.contradict_heard_legend(
            self.listener,
            self.legend[
                "legend_id"
            ]
        )

        self.listener[
            "current_layer"
        ] = "meeting_place"

        result = (
            CatExplorationPlanner
            .choose_destination(
                cat=self.listener,
                universe=self.universe
            )
        )

        heard_candidates = [
            candidate
            for candidate
            in result["candidates"]
            if candidate.get(
                "source"
            ) == "heard_legend"
        ]

        self.assertEqual(
            heard_candidates,
            []
        )


if __name__ == "__main__":
    unittest.main()