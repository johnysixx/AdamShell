from core.entity.components import SpatialVector3
import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_perception import CatPerception
from cats.cat_perception_state import (
    CatBarObservation,
)


class CatBarObservationObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="bar_observer",
            color="black",
            fur_length="short",
        )

        self.cat.position = SpatialVector3(x=0.0, y=0.0, z=0.0)

        self.perception = CatPerception(
            self.cats
        )

    def observe_bar(self):
        return self.perception._observe_bar(
            cat=self.cat,
            position=self.cat.position,
            radius=10.0,
        )

    def test_bar_observation_is_object(
        self
    ):
        observation = self.observe_bar()

        self.assertIsInstance(
            observation,
            CatBarObservation,
        )

        self.assertFalse(
            hasattr(
                observation,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                observation,
                "__getitem__",
            )
        )

    def test_missing_quantum_space_has_explicit_state(
        self
    ):
        self.universe.quantum_space = None

        observation = self.observe_bar()

        self.assertFalse(
            observation.visible
        )

        self.assertIsNone(
            observation.distance
        )

        self.assertIsInstance(
            observation.known,
            bool,
        )

    def test_bar_memory_makes_missing_bar_known(
        self
    ):
        self.universe.quantum_space = None

        self.cat.memory.remember(
            event_type="bar_entry",
            location="bar",
        )

        observation = self.observe_bar()

        self.assertTrue(
            observation.known
        )

        self.assertFalse(
            observation.visible
        )

        self.assertIsNone(
            observation.distance
        )


if __name__ == "__main__":
    unittest.main()
