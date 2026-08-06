import unittest

from universe.universe import Universe
from cats.cats import Cats
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J
)


class StableCatExplorationBoxPairTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.creator = self.cats.create_cat(
            name="creator",
            color="black",
            fur_length="short"
        )

        self.other_cat = self.cats.create_cat(
            name="other_cat",
            color="gray",
            fur_length="short"
        )

        for cat in (
            self.creator,
            self.other_cat
        ):
            cat["current_layer"] = (
                "meeting_place"
            )

            cat["position"] = {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }

            cat["idea_energy"] = (
                QUANTUM_BOX_ENERGY_COST_J
                * 10.0
            )

        result = (
            self.universe
            .cat_box_transfer
            .create_exploration_pair(
                cat=self.creator,
                destination_layer=(
                    "quantum_layer"
                ),
                destination_position={
                    "x": 8.0,
                    "y": 2.0,
                    "z": -1.0
                }
            )
        )

        self.source = result[
            "source_box"
        ]

        self.target = result[
            "target_box"
        ]

    def transfer(
        self,
        cat,
        source,
        target
    ):
        return (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=cat,
                source_box_id=source.id,
                target_box_id=target.id
            )
        )

    def test_creator_departure_keeps_pair(
        self
    ):
        result = self.transfer(
            self.creator,
            self.source,
            self.target
        )

        self.assertTrue(
            result["transferred"]
        )

        self.assertTrue(
            result["pair_remains_stable"]
        )

        self.assertIn(
            self.source,
            self.universe.quantum_boxes
        )

        self.assertIn(
            self.target,
            self.universe.quantum_boxes
        )

    def test_other_cat_can_use_pair(
        self
    ):
        result = self.transfer(
            self.other_cat,
            self.source,
            self.target
        )

        self.assertTrue(
            result["transferred"]
        )

        self.assertTrue(
            result["pair_remains_stable"]
        )

    def test_other_cat_return_keeps_pair(
        self
    ):
        self.transfer(
            self.other_cat,
            self.source,
            self.target
        )

        result = self.transfer(
            self.other_cat,
            self.target,
            self.source
        )

        self.assertTrue(
            result["pair_remains_stable"]
        )

        self.assertIn(
            self.source,
            self.universe.quantum_boxes
        )

        self.assertIn(
            self.target,
            self.universe.quantum_boxes
        )

    def test_creator_return_dissolves_pair(
        self
    ):
        self.transfer(
            self.creator,
            self.source,
            self.target
        )

        result = self.transfer(
            self.creator,
            self.target,
            self.source
        )

        self.assertTrue(
            result["creator_returned"]
        )

        self.assertFalse(
            result["pair_remains_stable"]
        )

        dissolution = result[
            "pair_dissolution"
        ]

        self.assertTrue(
            dissolution["dissolved"]
        )

        self.assertNotIn(
            self.source,
            self.universe.quantum_boxes
        )

        self.assertNotIn(
            self.target,
            self.universe.quantum_boxes
        )

    def test_dissolution_conserves_energy(
        self
    ):
        self.transfer(
            self.creator,
            self.source,
            self.target
        )

        result = self.transfer(
            self.creator,
            self.target,
            self.source
        )

        dissolution = result[
            "pair_dissolution"
        ]

        self.assertTrue(
            dissolution["energy_conserved"]
        )

        self.assertAlmostEqual(
            dissolution["energy_total_j"],
            dissolution[
                "energy_distributed_j"
            ]
        )

    def test_quantum_remote_share_becomes_dark_energy(
        self
    ):
        self.transfer(
            self.creator,
            self.source,
            self.target
        )

        result = self.transfer(
            self.creator,
            self.target,
            self.source
        )

        dissolution = result[
            "pair_dissolution"
        ]

        total = dissolution[
            "energy_total_j"
        ]

        self.assertAlmostEqual(
            dissolution[
                "quantum_dark_energy_j"
            ],
            total * 0.30
        )

        self.assertEqual(
            dissolution[
                "remote_layer_energy_j"
            ],
            0.0
        )

    def test_dissolution_creates_cronenberg(
        self
    ):
        before = len(
            self.universe.cronenbergs
        )

        self.transfer(
            self.creator,
            self.source,
            self.target
        )

        result = self.transfer(
            self.creator,
            self.target,
            self.source
        )

        self.assertEqual(
            len(
                self.universe.cronenbergs
            ),
            before + 1
        )

        dissolution = result[
            "pair_dissolution"
        ]

        self.assertAlmostEqual(
            dissolution[
                "cronenberg"
            ][
                "energy_j"
            ],
            dissolution[
                "energy_total_j"
            ] * 0.20
        )


if __name__ == "__main__":
    unittest.main()