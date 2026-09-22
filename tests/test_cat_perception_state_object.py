from core.entity.components import SpatialVector3
import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_mind import CatMind
from cats.cat_perception_state import (
    CatPerceptionFailure,
    CatPerceptionState,
)


class CatPerceptionStateObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="perception_object_cat",
            color="black",
            fur_length="short",
        )

        self.cat.position = SpatialVector3(x=0.0, y=0.0, z=0.0)

    def test_observe_returns_object_state(
        self
    ):
        observations = (
            self.cats.observe_cat(
                self.cat
            )
        )

        self.assertIsInstance(
            observations,
            CatPerceptionState,
        )

        self.assertFalse(
            hasattr(
                observations,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                observations,
                "__getitem__",
            )
        )

    def test_mind_rejects_mapping_observations(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            CatMind.consider(
                self.cat,
                {
                    "bar_known": True,
                },
            )

    def test_invalid_observation_is_object_failure(
        self
    ):
        failure = (
            self.cats.observe_cat(
                None
            )
        )

        self.assertIsInstance(
            failure,
            CatPerceptionFailure,
        )

        self.assertFalse(
            failure.observed
        )

        self.assertEqual(
            failure.reason,
            "invalid_cat",
        )


if __name__ == "__main__":
    unittest.main()
