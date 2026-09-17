import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_perception_state import (
    CatNearbyCatObservation,
)


class CatNearbyCatObservationObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.observer = self.cats.create_cat(
            name="observer",
            color="black",
            fur_length="short",
        )

        self.observer.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

    def create_cat(
        self,
        name,
        x,
    ):
        cat = self.cats.create_cat(
            name=name,
            color="gray",
            fur_length="short",
        )

        cat.position = {
            "x": float(x),
            "y": 0.0,
            "z": 0.0,
        }

        return cat

    def test_nearby_cat_detail_is_object(
        self
    ):
        nearby = self.create_cat(
            "nearby",
            2.0,
        )

        observations = (
            self.cats.observe_cat(
                self.observer
            )
        )

        detail = next(
            item
            for item
            in observations.nearby_cat_details
            if item.name == nearby.name
        )

        self.assertIsInstance(
            detail,
            CatNearbyCatObservation,
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

    def test_nearby_cat_detail_exposes_fields(
        self
    ):
        nearby = self.create_cat(
            "nearby",
            3.0,
        )

        observations = (
            self.cats.observe_cat(
                self.observer
            )
        )

        detail = next(
            item
            for item
            in observations.nearby_cat_details
            if item.name == nearby.name
        )

        self.assertEqual(
            detail.name,
            nearby.name,
        )

        self.assertEqual(
            detail.distance,
            3.0,
        )

        self.assertEqual(
            detail.position,
            nearby.position,
        )

        self.assertIsNot(
            detail.position,
            nearby.position,
        )

    def test_nearby_cat_details_are_sorted_by_distance(
        self
    ):
        self.create_cat(
            "farther",
            4.0,
        )

        self.create_cat(
            "closer",
            1.0,
        )

        observations = (
            self.cats.observe_cat(
                self.observer
            )
        )

        names = [
            detail.name
            for detail
            in observations.nearby_cat_details
        ]

        self.assertEqual(
            names[:2],
            [
                "closer",
                "farther",
            ],
        )


if __name__ == "__main__":
    unittest.main()
