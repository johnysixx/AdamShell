import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_perception import CatPerception
from cats.cat_mind import CatMind
from universe.aroma_residue import AromaResidue
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J
)


class CatScentReorientationAfterTransferTests(
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

        self.cats.learn_cat_aroma(
            observer=self.tracker,
            observed_cat=self.creator
        )

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

        # Další lokální stopa v cílové vrstvě.
        self.trail_box = (
            self.universe
            .create_quantum_box(
                layer="quantum_layer"
            )
        )

        self.trail_box.position = {
            "x": 9.0,
            "y": 0.0,
            "z": 0.0
        }

        AromaResidue.transfer(
            source_profile=(
                self.creator[
                    "aroma"
                ]
            ),
            target=self.trail_box,
            source_identity="creator",
            fraction=0.30
        )

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

    def transfer_tracker(self):
        result = None

        for _ in range(20):
            result = (
                self.cats
                .execute_cat_intention(
                    self.tracker
                )
            )

            if result["name"] == (
                "cat_followed_scent_"
                "through_box"
            ):
                return result

        self.fail(
            "Tracker nedokončil průchod boxem."
        )

    def test_new_layer_is_freshly_perceived_and_sniffed(
        self
    ):
        transfer = self.transfer_tracker()

        self.assertTrue(
            transfer[
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

        # Starý intention je dokončený.
        self.assertIsNone(
            self.tracker[
                "mind"
            ][
                "current_intention"
            ]
        )

        perception = CatPerception(
            self.cats
        )

        observations = perception.observe(
            self.tracker
        )

        self.assertEqual(
            observations[
                "current_layer"
            ],
            "quantum_layer"
        )

        smelled = {
            item["entity_id"]: item
            for item
            in observations[
                "olfaction"
            ][
                "detected_aromas"
            ]
        }

        self.assertIn(
            self.trail_box.id,
            smelled
        )

        trail_smell = smelled[
            self.trail_box.id
        ]

        self.assertTrue(
            trail_smell[
                "recognition"
            ][
                "recognized"
            ]
        )

        self.assertEqual(
            trail_smell[
                "recognition"
            ][
                "identity"
            ],
            "cat:creator"
        )

        memories = observations[
            "scent_memories"
        ]

        trail_memories = [
            memory
            for memory in memories
            if memory.get(
                "source_id"
            ) == self.trail_box.id
        ]

        self.assertEqual(
            len(trail_memories),
            1
        )

        self.assertEqual(
            trail_memories[0][
                "layer"
            ],
            "quantum_layer"
        )


    def test_cat_makes_fresh_decision_from_local_scent(
        self
    ):
        self.transfer_tracker()

        self.assertIsNone(
            self.tracker[
                "mind"
            ][
                "current_intention"
            ]
        )

        perception = CatPerception(
            self.cats
        )

        observations = perception.observe(
            self.tracker
        )

        # Izolujeme pr?v? pachov? rozhodnut?.
        # Perception z?st?v? skute?n?, jen
        # odstra?ujeme konkuren?n? podn?ty,
        # kter? tento test netestuje.
        observations[
            "bar_known"
        ] = False

        observations[
            "bar_visible"
        ] = False

        observations[
            "unexplored_boxes"
        ] = []

        observations[
            "can_create_exploration_pair"
        ] = False

        observations[
            "nearby_cats"
        ] = []

        observations[
            "shareable_legend_count"
        ] = 0

        observations[
            "interesting_unknown"
        ] = False

        observations[
            "huntable_cronenbergs"
        ] = []

        observations[
            "visible_cronenbergs"
        ] = []

        observations[
            "cronenberg_scent_recognized"
        ] = False

        traits = self.tracker[
            "personality"
        ][
            "traits"
        ]

        traits["curiosity"] = 1.0
        traits["courage"] = 1.0
        traits["patience"] = 0.0

        decision = CatMind.decide(
            cat=self.tracker,
            observations=observations
        )

        self.assertTrue(
            decision["selected"]
        )

        self.assertEqual(
            decision["intention"],
            "follow_known_scent"
        )

        self.assertEqual(
            decision[
                "target"
            ][
                "identity"
            ],
            "cat:creator"
        )

        self.assertEqual(
            decision[
                "target"
            ][
                "layer"
            ],
            "quantum_layer"
        )

        self.assertEqual(
            decision[
                "target"
            ][
                "source_id"
            ],
            self.trail_box.id
        )

        self.assertEqual(
            decision[
                "target"
            ][
                "position"
            ],
            self.trail_box.position
        )

        # A hlavn?: toto je NOV? intention.
        self.assertEqual(
            self.tracker[
                "mind"
            ][
                "current_intention"
            ][
                "type"
            ],
            "follow_known_scent"
        )


if __name__ == "__main__":
    unittest.main()