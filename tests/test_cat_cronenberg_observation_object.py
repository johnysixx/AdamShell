import unittest

from universe.universe import Universe
from core.entity.components import SpatialVector3
from cats.cats import Cats
from cats.cat_perception_state import (
    CatCronenbergObservation,
)


class CatCronenbergObservationObjectTests(
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
            fur_length="short",
        )

        self.cat.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

    def create_cronenberg(
        self,
        size,
        x,
    ):
        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Observation test."
                ),
                source_component="test",
                source_operation="perception",
            )
        )

        cronenberg.size = float(size)

        cronenberg.position = SpatialVector3(
            x=float(x),
            y=0.0,
            z=0.0,
        )

        return cronenberg

    def test_visible_cronenberg_detail_is_object(
        self
    ):
        cronenberg = self.create_cronenberg(
            size=2.0,
            x=2.0,
        )

        observations = (
            self.cats.observe_cat(
                self.cat
            )
        )

        detail = next(
            item
            for item
            in observations.visible_cronenberg_details
            if item.id == cronenberg.id
        )

        self.assertIsInstance(
            detail,
            CatCronenbergObservation,
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

        self.assertIsNone(
            detail.size_ratio
        )

    def test_huntable_cronenberg_has_size_ratio(
        self
    ):
        cronenberg = self.create_cronenberg(
            size=0.8,
            x=2.0,
        )

        observations = (
            self.cats.observe_cat(
                self.cat
            )
        )

        detail = next(
            item
            for item
            in observations.huntable_cronenberg_details
            if item.id == cronenberg.id
        )

        self.assertIsInstance(
            detail,
            CatCronenbergObservation,
        )

        self.assertIsNotNone(
            detail.size_ratio
        )

        self.assertEqual(
            detail.size_ratio,
            detail.size / self.cat.size,
        )

    def test_visible_cronenbergs_are_sorted_by_distance(
        self
    ):
        farther = self.create_cronenberg(
            size=2.0,
            x=4.0,
        )

        closer = self.create_cronenberg(
            size=2.0,
            x=1.0,
        )

        observations = (
            self.cats.observe_cat(
                self.cat
            )
        )

        ids = [
            detail.id
            for detail
            in observations.visible_cronenberg_details
        ]

        self.assertLess(
            ids.index(closer.id),
            ids.index(farther.id),
        )


if __name__ == "__main__":
    unittest.main()
