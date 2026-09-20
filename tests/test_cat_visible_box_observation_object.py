import unittest
from core.entity.components import SpatialVector3

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_perception import CatPerception
from cats.cat_perception_state import (
    CatVisibleBoxObservation,
)


class CatVisibleBoxObservationObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="box_observer",
            color="black",
            fur_length="short",
        )

        self.cat.current_layer = (
            "quantum_layer"
        )

        self.cat.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

        self.box = (
            self.universe
            .create_quantum_box()
        )

        self.box.current_layer = (
            "quantum_layer"
        )

        self.box.position = SpatialVector3(x=3.0, y=0.0, z=0.0)

    def box_detail(self):
        observations = (
            CatPerception(
                self.cats
            )
            .observe(
                self.cat
            )
        )

        return next(
            detail
            for detail
            in observations.visible_box_details
            if detail.id == self.box.id
        )

    def test_visible_box_detail_is_object(
        self
    ):
        detail = self.box_detail()

        self.assertIsInstance(
            detail,
            CatVisibleBoxObservation,
        )

        self.assertFalse(
            hasattr(
                detail,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                detail,
                "__getitem__",
            )
        )

    def test_unexplored_box_has_explicit_unknown_state(
        self
    ):
        detail = self.box_detail()

        self.assertFalse(
            detail.explored
        )

        self.assertIsNone(
            detail.state
        )

        self.assertIsNone(
            detail.collapsed
        )

        self.assertIsNone(
            detail.recognized_as_quantum_box
        )

        self.assertIsNone(
            detail.paired
        )

        self.assertIsNone(
            detail.counterpart_known
        )

    def test_box_observation_does_not_expose_route(
        self
    ):
        detail = self.box_detail()

        self.assertFalse(
            hasattr(
                detail,
                "counterpart_box_id",
            )
        )

        self.assertFalse(
            hasattr(
                detail,
                "target_layer",
            )
        )

        self.assertFalse(
            hasattr(
                detail,
                "quantum_counterpart",
            )
        )


if __name__ == "__main__":
    unittest.main()
