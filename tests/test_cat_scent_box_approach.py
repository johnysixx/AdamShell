import unittest

from universe.universe import Universe
from cats.cats import Cats
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J
)


class CatScentBoxApproachTests(
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

        self.tracker = self.cats.create_cat(
            name="tracker",
            color="gray",
            fur_length="short"
        )

        self.creator[
            "current_layer"
        ] = "meeting_place"

        self.creator["position"] = {
            "x": 3.0,
            "y": 0.0,
            "z": 0.0
        }

        self.creator["idea_energy"] = (
            QUANTUM_BOX_ENERGY_COST_J
            * 10.0
        )

        self.tracker[
            "current_layer"
        ] = "meeting_place"

        self.tracker["position"] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        creation = (
            self.universe
            .cat_box_transfer
            .create_exploration_pair(
                cat=self.creator,
                destination_layer=(
                    "quantum_layer"
                ),
                destination_position={
                    "x": 8.0,
                    "y": 0.0,
                    "z": 0.0
                },
                source_position={
                    "x": 3.0,
                    "y": 0.0,
                    "z": 0.0
                }
            )
        )

        self.source = creation[
            "source_box"
        ]

        self.target = creation[
            "target_box"
        ]

        self.tracker[
            "mind"
        ][
            "current_intention"
        ] = {
            "type": (
                "follow_scent_through_box"
            ),
            "target": {
                "identity": "cat:creator",
                "box_id": self.source.id,
                "counterpart_box_id": (
                    self.target.id
                ),
                "source_layer": (
                    "meeting_place"
                ),
                "target_layer": (
                    "quantum_layer"
                )
            },
            "score": 1.0,
            "reasons": ["test"]
        }

    def test_cat_walks_to_box_before_transfer(
        self
    ):
        first = (
            self.cats
            .execute_cat_intention(
                self.tracker
            )
        )

        self.assertEqual(
            first["name"],
            "cat_following_scent_to_box"
        )

        self.assertEqual(
            self.tracker[
                "current_layer"
            ],
            "meeting_place"
        )

        self.assertEqual(
            self.tracker["position"],
            {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            }
        )

        self.assertIsNotNone(
            self.tracker[
                "mind"
            ][
                "current_intention"
            ]
        )

        self.assertTrue(
            self.tracker[
                "scent_box_follow"
            ][
                "active"
            ]
        )

        last = first

        for _ in range(10):
            last = (
                self.cats
                .execute_cat_intention(
                    self.tracker
                )
            )

            if last["name"] == (
                "cat_followed_scent_"
                "through_box"
            ):
                break

        self.assertEqual(
            last["name"],
            (
                "cat_followed_scent_"
                "through_box"
            )
        )

        self.assertTrue(
            last[
                "transfer"
            ][
                "transferred"
            ]
        )

        self.assertEqual(
            self.tracker[
                "current_layer"
            ],
            "quantum_layer"
        )

        self.assertIsNone(
            self.tracker[
                "mind"
            ][
                "current_intention"
            ]
        )

        self.assertTrue(
            self.tracker[
                "scent_box_follow"
            ][
                "arrived_at_box"
            ]
        )

    def test_cat_already_at_box_transfers_immediately(
        self
    ):
        self.tracker["position"] = dict(
            self.source.position
        )

        result = (
            self.cats
            .execute_cat_intention(
                self.tracker
            )
        )

        self.assertEqual(
            result["name"],
            (
                "cat_followed_scent_"
                "through_box"
            )
        )

        self.assertTrue(
            result[
                "transfer"
            ][
                "transferred"
            ]
        )

        self.assertEqual(
            self.tracker[
                "current_layer"
            ],
            "quantum_layer"
        )


if __name__ == "__main__":
    unittest.main()