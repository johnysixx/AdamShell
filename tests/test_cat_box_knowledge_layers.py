import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_perception import CatPerception


class CatBoxKnowledgeLayerTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="observer",
            color="black",
            fur_length="short"
        )

        self.cat[
            "current_layer"
        ] = "quantum_layer"

        self.cat["position"] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        self.box = (
            self.universe
            .create_quantum_box()
        )

        self.box.current_layer = (
            "quantum_layer"
        )

        self.box.position = {
            "x": 3.0,
            "y": 0.0,
            "z": 0.0
        }

    def _box_detail(
        self
    ):
        observed = CatPerception(
            self.cats
        ).observe(
            self.cat
        )

        return next(
            item
            for item
            in observed[
                "visible_box_details"
            ]
            if item["id"] == self.box.id
        )

    def test_distant_box_hides_quantum_internal_state(
        self
    ):
        detail = self._box_detail()

        self.assertFalse(
            detail[
                "explored"
            ]
        )

        self.assertNotIn(
            "state",
            detail
        )

        self.assertNotIn(
            "collapsed",
            detail
        )

        self.assertNotIn(
            "recognized_as_quantum_box",
            detail
        )

        self.assertIn(
            "position",
            detail
        )

        self.assertIn(
            "distance",
            detail
        )

        self.assertIn(
            "occupied",
            detail
        )

    def test_explored_box_reveals_quantum_state(
        self
    ):
        self.cat[
            "mind"
        ][
            "current_intention"
        ] = {
            "type": "explore_box",
            "target": self.box.id,
            "score": 1.0,
            "reasons": [
                "test"
            ]
        }

        result = (
            self.cats
            .execute_cat_intention(
                self.cat
            )
        )

        for _ in range(10):
            if result["name"] == (
                "cat_explored_quantum_box"
            ):
                break

            result = (
                self.cats
                .execute_cat_intention(
                    self.cat
                )
            )

        self.assertEqual(
            result["name"],
            "cat_explored_quantum_box"
        )

        detail = self._box_detail()

        self.assertTrue(
            detail[
                "explored"
            ]
        )

        self.assertIn(
            "state",
            detail
        )

        self.assertIn(
            "collapsed",
            detail
        )

        self.assertTrue(
            detail[
                "recognized_as_quantum_box"
            ]
        )

    def test_exploration_does_not_reveal_counterpart(
        self
    ):
        detail = self._box_detail()

        self.assertNotIn(
            "quantum_counterpart",
            detail
        )

        self.assertNotIn(
            "counterpart_box_id",
            detail
        )

        self.assertNotIn(
            "target_layer",
            detail
        )


if __name__ == "__main__":
    unittest.main()
