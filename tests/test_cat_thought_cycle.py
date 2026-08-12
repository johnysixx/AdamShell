import unittest

from universe.universe import Universe
from cats.cats import Cats


class CatThoughtCycleTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="autonomous_cat",
            color="black",
            fur_length="short"
        )

        self.cat["position"] = {
            "x": 1.0,
            "y": 0.0,
            "z": 0.0
        }

    def test_cat_can_think_and_start_bar_route(
        self
    ):
        # Bar je blízko a nejsou přítomné
        # jiné výrazné možnosti.
        result = self.cats.think_and_act(
            cat=self.cat
        )

        self.assertTrue(
            result["completed"]
        )

        self.assertEqual(
            result[
                "decision"
            ][
                "intention"
            ],
            "visit_bar"
        )

        self.assertTrue(
            result[
                "execution"
            ][
                "executed"
            ]
        )

        self.assertEqual(
            self.cat["intent"],
            "return_to_bar"
        )

    def test_curious_cat_notices_new_box(
        self
    ):
        self.cat[
            "personality"
        ][
            "traits"
        ][
            "curiosity"
        ] = 1.0

        box = self.universe.create_quantum_box()

        box.position = {
            "x": 1.5,
            "y": 0.0,
            "z": 0.0
        }

        result = self.cats.think_and_act(
            cat=self.cat
        )

        self.assertEqual(
            result[
                "decision"
            ][
                "intention"
            ],
            "explore_box"
        )

        self.assertTrue(
            result[
                "execution"
            ][
                "executed"
            ]
        )

        self.assertEqual(
            result[
                "execution"
            ][
                "name"
            ],
            "cat_approaching_box_to_explore"
        )

        self.assertEqual(
            result[
                "execution"
            ][
                "box_id"
            ],
            box.id
        )

    def test_missing_position_stops_cycle(
        self
    ):
        self.cat.pop(
            "position"
        )

        result = self.cats.think_and_act(
            cat=self.cat
        )

        self.assertFalse(
            result["completed"]
        )

        self.assertEqual(
            result[
                "observation"
            ][
                "reason"
            ],
            "cat_has_no_position"
        )


if __name__ == "__main__":
    unittest.main()