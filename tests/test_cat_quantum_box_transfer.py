import unittest

from universe.universe import Universe
from cats.cats import Cats
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J
)


class CatQuantumBoxTransferTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="traveller",
            color="black",
            fur_length="short"
        )

        self.cat.current_layer = (
            "meeting_place"
        )

        self.cat.position = {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }

        self.source = (
            self.universe.create_quantum_box(
                layer="meeting_place"
            )
        )

        self.target = (
            self.universe.create_quantum_box(
                layer="quantum_layer"
            )
        )

        self.source.position = {
            "x": 1.0,
            "y": 1.0,
            "z": 1.0
        }

        self.target.position = {
            "x": 8.0,
            "y": 4.0,
            "z": -2.0
        }

        self.universe.cat_box_transfer\
            .pair_boxes(
                self.source,
                self.target
            )

    def test_boxes_are_paired_between_layers(
        self
    ):
        self.assertTrue(
            self.source
            .quantum_counterpart[
                "paired"
            ]
        )

        self.assertEqual(
            self.source
            .quantum_counterpart[
                "box_id"
            ],
            self.target.id
        )

    def test_cat_transfers_to_target_layer(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                cat=self.cat,
                source_box_id=(
                    self.source.id
                ),
                target_box_id=(
                    self.target.id
                )
            )
        )

        self.assertTrue(
            result["transferred"]
        )

        self.assertEqual(
            self.cat.current_layer,
            "quantum_layer"
        )

        self.assertEqual(
            self.cat.position,
            self.target.position
        )

    def test_target_box_is_consumed(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                self.cat,
                self.source.id,
                self.target.id
            )
        )

        self.assertTrue(
            result[
                "target_box_consumed"
            ]
        )

        self.assertNotIn(
            self.target,
            self.universe.quantum_boxes
        )

        self.assertIn(
            self.source,
            self.universe.quantum_boxes
        )

    def test_consumed_energy_does_not_enter_dark_sector(
        self
    ):
        dark_sector = getattr(
            self.universe,
            "dark_sector",
            None
        )

        before = (
            dark_sector.dark_energy_j
            if dark_sector is not None
            else 0.0
        )

        self.universe.cat_box_transfer\
            .transfer_cat(
                self.cat,
                self.source.id,
                self.target.id
            )

        after = (
            dark_sector.dark_energy_j
            if dark_sector is not None
            else 0.0
        )

        self.assertEqual(
            before,
            after
        )

    def test_cat_can_create_return_counterpart(
        self
    ):
        self.universe.cat_box_transfer\
            .transfer_cat(
                self.cat,
                self.source.id,
                self.target.id
            )

        self.cat.idea_energy = (
            QUANTUM_BOX_ENERGY_COST_J
            + 10.0
        )

        result = (
            self.universe
            .cat_box_transfer
            .create_return_counterpart(
                cat=self.cat,
                source_box_id=(
                    self.source.id
                )
            )
        )

        self.assertTrue(
            result["created"]
        )

        counterpart = result[
            "counterpart"
        ]

        self.assertEqual(
            counterpart.current_layer,
            "quantum_layer"
        )

        self.assertEqual(
            counterpart.position,
            self.cat.position
        )

        self.assertTrue(
            self.source
            .quantum_counterpart[
                "paired"
            ]
        )

    def test_transfer_creates_quantum_trail(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .transfer_cat(
                self.cat,
                self.source.id,
                self.target.id
            )
        )

        self.assertEqual(
            len(
                self.universe
                .quantum_cat_trails
            ),
            1
        )

        self.assertEqual(
            result[
                "trail"
            ][
                "cat"
            ],
            "traveller"
        )

    def test_cat_stabilizes_direct_path(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .stabilize_direct_trail(
                self.cat,
                {
                    "x": 10.0,
                    "y": 0.0,
                    "z": 0.0
                }
            )
        )

        self.assertTrue(
            result["stabilized"]
        )

        self.assertEqual(
            result["path_kind"],
            "most_direct_possible"
        )


if __name__ == "__main__":
    unittest.main()