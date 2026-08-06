import unittest

from universe.universe import Universe
from cats.cats import Cats


class QuantumBoxTransferVisibilityTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.traveller = self.cats.create_cat(
            name="traveller",
            color="black",
            fur_length="short"
        )

        self.observer_cat = self.cats.create_cat(
            name="observer_cat",
            color="gray",
            fur_length="short"
        )

        self.human = {
            "name": "human_observer",
            "type": "human"
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
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        self.target.position = {
            "x": 1.0,
            "y": 0.0,
            "z": 0.0
        }

        self.observer_cat["position"] = {
            "x": 0.5,
            "y": 0.0,
            "z": 0.0
        }

        self.universe.cat_box_transfer\
            .pair_boxes(
                self.source,
                self.target
            )

        self.source.begin_cat_transfer(
            cat=self.traveller,
            target_box=self.target,
            tick=0
        )

    def test_transfer_box_is_hidden_from_human(
        self
    ):
        self.assertFalse(
            self.source.is_visible_to(
                self.human
            )
        )

        self.assertFalse(
            self.target.is_visible_to(
                self.human
            )
        )

    def test_transfer_box_is_visible_to_cat(
        self
    ):
        self.assertTrue(
            self.source.is_visible_to(
                self.observer_cat
            )
        )

        self.assertTrue(
            self.target.is_visible_to(
                self.observer_cat
            )
        )

    def test_cat_recognizes_occupied_box(
        self
    ):
        state = (
            self.source
            .cat_observation_state(
                self.observer_cat
            )
        )

        self.assertTrue(
            state["visible"]
        )

        self.assertTrue(
            state["occupied"]
        )

        self.assertEqual(
            state["occupancy_state"],
            "cat_transfer_occupied"
        )

        self.assertFalse(
            state[
                "occupant_identity_visible"
            ]
        )

    def test_cat_perception_lists_occupied_box(
        self
    ):
        result = self.cats.observe_cat(
            self.observer_cat,
            vision_radius=5.0
        )

        self.assertIn(
            self.source.id,
            result[
                "occupied_transfer_boxes"
            ]
        )

        self.assertNotIn(
            self.source.id,
            result[
                "unexplored_boxes"
            ]
        )


if __name__ == "__main__":
    unittest.main()