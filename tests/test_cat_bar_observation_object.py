from core.entity.components import SpatialVector3
import unittest
from dataclasses import FrozenInstanceError, replace

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



    def test_bar_observation_is_frozen(self):
        observation = CatBarObservation(
            known=True,
            visible=True,
            distance=2.0,
        )

        changes = (
            ("known", False),
            ("visible", False),
            ("distance", 10.0),
        )

        for name, value in changes:
            with self.subTest(field=name):
                with self.assertRaises(FrozenInstanceError):
                    setattr(observation, name, value)

    def test_bar_observation_replacement_preserves_original(self):
        original = CatBarObservation(
            known=True,
            visible=False,
            distance=None,
        )

        updated = replace(
            original,
            visible=True,
            distance=3.0,
        )

        self.assertIsNot(original, updated)
        self.assertTrue(original.known)
        self.assertFalse(original.visible)
        self.assertIsNone(original.distance)

        self.assertTrue(updated.known)
        self.assertTrue(updated.visible)
        self.assertEqual(updated.distance, 3.0)

    def test_producer_returns_frozen_bar_observation(self):
        self.universe.quantum_space = None

        observation = self.observe_bar()

        self.assertIsInstance(
            observation,
            CatBarObservation,
        )

        self.assertFalse(observation.visible)
        self.assertIsNone(observation.distance)

        with self.assertRaises(FrozenInstanceError):
            observation.known = True

    def test_new_bar_observation_preserves_previous_snapshot(self):
        self.universe.quantum_space = None

        first = self.observe_bar()
        first_known = first.known

        self.cat.memory.remember(
            event_type="bar_entry",
            location="bar",
        )

        second = self.observe_bar()

        self.assertIsNot(first, second)
        self.assertFalse(first_known)
        self.assertEqual(first.known, first_known)
        self.assertFalse(first.visible)
        self.assertIsNone(first.distance)

        self.assertTrue(second.known)
        self.assertFalse(second.visible)
        self.assertIsNone(second.distance)


if __name__ == "__main__":
    unittest.main()
