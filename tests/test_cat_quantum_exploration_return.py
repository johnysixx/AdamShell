import unittest

from universe.universe import Universe
from cats.cats import Cats
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J
)


class CatQuantumExplorationReturnTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="returning_explorer",
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
                "x": 4.0,
                "y": 0.0,
                "z": 0.0
            }
        }

        traits = self.cat[
            "personality"
        ][
            "traits"
        ]

        # Tato kočka je po dosažení cíle
        # silně nakloněná návratu.
        traits["curiosity"] = 0.0
        traits["courage"] = 0.0
        traits["patience"] = 1.0

    def reach_goal(self):
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
                return result

        self.fail(
            "Kočka nedorazila k cíli."
        )

    def test_arrival_is_written_to_memory(
        self
    ):
        self.reach_goal()

        events = self.cat[
            "memory"
        ].events

        self.assertTrue(
            any(
                event.get(
                    "event_type"
                )
                == "successful_exploration"
                for event in events
            )
        )

    def test_cat_can_choose_return_after_exploration(
        self
    ):
        result = self.reach_goal()

        resolution = result[
            "arrival_resolution"
        ]

        self.assertEqual(
            resolution["action"],
            (
                "return_via_exploration_pair"
            )
        )

        self.assertTrue(
            resolution[
                "return_plan"
            ][
                "started"
            ]
        )

        self.assertTrue(
            self.cat[
                "quantum_return"
            ][
                "active"
            ]
        )

    def test_creator_eventually_returns_and_pair_dissolves(
        self
    ):
        self.reach_goal()

        for _ in range(100):
            result = (
                self.cats
                .advance_cat_quantum_return(
                    self.cat
                )
            )

            transfer = result.get(
                "transfer_result"
            )

            if (
                transfer is not None
                and transfer.get(
                    "transferred",
                    False
                )
            ):
                break

        self.assertEqual(
            self.cat["current_layer"],
            "meeting_place"
        )

        self.assertEqual(
            self.cat["state"],
            (
                "returned_from_"
                "quantum_exploration"
            )
        )

        self.assertEqual(
            len(
                [
                    pair
                    for pair
                    in self.universe
                    .stable_cat_box_pairs
                    if pair.get(
                        "active",
                        False
                    )
                ]
            ),
            0
        )

        self.assertGreaterEqual(
            len(
                self.universe.cronenbergs
            ),
            1
        )


if __name__ == "__main__":
    unittest.main()