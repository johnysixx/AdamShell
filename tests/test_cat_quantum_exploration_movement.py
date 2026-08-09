import unittest

from universe.universe import Universe
from cats.cats import Cats
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J
)


class CatQuantumExplorationMovementTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="quantum_explorer",
            color="black",
            fur_length="short"
        )

        self.cat["current_layer"] = (
            "meeting_place"
        )

        self.cat["position"] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        self.cat["idea_energy"] = (
            QUANTUM_BOX_ENERGY_COST_J
            * 10.0
        )

        self.cat["exploration_goal"] = {
            "layer": "quantum_layer",
            "position": {
                "x": 6.0,
                "y": 0.0,
                "z": 0.0
            }
        }

        self.cat[
            "personality"
        ][
            "traits"
        ][
            "curiosity"
        ] = 1.0

    def test_pair_entry_is_not_final_destination(
        self
    ):
        result = self.cats.think_and_act(
            cat=self.cat
        )

        self.assertTrue(
            result["completed"]
        )

        self.assertEqual(
            self.cat["current_layer"],
            "quantum_layer"
        )

        self.assertNotEqual(
            self.cat["position"],
            {
                "x": 6.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        exploration = self.cat[
            "quantum_exploration"
        ]

        self.assertTrue(
            exploration["active"]
        )

        self.assertEqual(
            exploration["destination"],
            {
                "x": 6.0,
                "y": 0.0,
                "z": 0.0
            }
        )

    def test_quantum_route_is_most_direct_possible(
        self
    ):
        self.cats.think_and_act(
            cat=self.cat
        )

        exploration = self.cat[
            "quantum_exploration"
        ]

        self.assertEqual(
            exploration[
                "stabilized_path"
            ][
                "path_kind"
            ],
            "most_direct_possible"
        )

    def test_cat_advances_along_quantum_route(
        self
    ):
        self.cats.think_and_act(
            cat=self.cat
        )

        start = dict(
            self.cat["position"]
        )

        result = (
            self.cats
            .advance_cat_quantum_exploration(
                self.cat
            )
        )

        self.assertTrue(
            result["advanced"]
        )

        self.assertNotEqual(
            self.cat["position"],
            start
        )

    def test_cat_eventually_reaches_goal(
        self
    ):
        self.cats.think_and_act(
            cat=self.cat
        )

        for _ in range(100):
            result = (
                self.cats
                .advance_cat_quantum_exploration(
                    self.cat
                )
            )

            if result.get(
                "arrived",
                False
            ):
                break

        self.assertTrue(
            result["arrived"]
        )

        history = self.cat[
            "quantum_exploration_history"
        ]

        self.assertGreaterEqual(
            len(history),
            1
        )

        self.assertTrue(
            history[-1]["arrived"]
        )

        self.assertEqual(
            history[-1]["destination"],
            {
                "x": 6.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.assertEqual(
            self.cat["position"],
            {
                "x": 6.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.assertIsNotNone(
            result.get(
                "arrival_resolution"
            )
        )

        self.assertTrue(
            result[
                "arrival_resolution"
            ][
                "resolved"
            ]
        )


if __name__ == "__main__":
    unittest.main()