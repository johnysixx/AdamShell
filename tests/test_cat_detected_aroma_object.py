from core.entity.components import SpatialVector3
import unittest
from dataclasses import FrozenInstanceError, replace
from universe.aroma_composition import AromaComposition

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_olfaction import CatOlfaction
from cats.cat_olfaction_state import (
    CatAromaRecognition,
    CatDetectedAroma,
)


class CatDetectedAromaObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.observer = self.cats.create_cat(
            name="observer",
            color="black",
            fur_length="short",
        )

        self.other = self.cats.create_cat(
            name="pazuzu",
            color="white",
            fur_length="short",
        )

        self.observer.position = SpatialVector3(x=0.0, y=0.0, z=0.0)

        self.other.position = SpatialVector3(x=2.0, y=0.0, z=0.0)

        self.universe.entities.append(
            self.other
        )

    def detected(self):
        result = CatOlfaction.sniff(
            self.observer,
            self.universe,
        )

        return next(
            item
            for item in result.detected_aromas
            if item.actual_identity
            == "cat:pazuzu"
        )

    def test_detected_aroma_is_object(
        self
    ):
        detected = self.detected()

        self.assertIsInstance(
            detected,
            CatDetectedAroma,
        )

        self.assertFalse(
            hasattr(
                detected,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                detected,
                "__getitem__",
            )
        )

    def test_detected_aroma_contains_recognition_object(
        self
    ):
        detected = self.detected()

        self.assertIsInstance(
            detected.recognition,
            CatAromaRecognition,
        )

        self.assertEqual(
            detected.actual_identity,
            "cat:pazuzu",
        )

        self.assertGreater(
            detected.perceived_intensity,
            0.0,
        )

    def test_chemical_components_are_object_state(
        self
    ):
        detected = self.detected()

        self.assertIsInstance(
            detected.components,
            AromaComposition,
        )

        self.assertIsInstance(
            detected.raw_components,
            AromaComposition,
        )

        for composition in (
            detected.components,
            detected.raw_components,
        ):
            self.assertFalse(
                hasattr(
                    composition,
                    "get",
                )
            )

            with self.assertRaises(TypeError):
                _ = composition["cat"]

        self.assertGreater(
            detected.components.amount(
                "cat"
            ),
            0.0,
        )

        self.assertGreater(
            detected.raw_components.amount(
                "cat"
            ),
            0.0,
        )




    def test_detected_aroma_is_frozen(self):
        detected = self.detected()

        changes = (
            ("entity_id", "other"),
            ("actual_identity", "other"),
            ("position", SpatialVector3.zero()),
            ("distance", 0.0),
            ("components", AromaComposition.empty()),
            ("raw_components", AromaComposition.empty()),
            ("perceived_intensity", 0.0),
            ("recognition", CatAromaRecognition()),
        )

        for name, value in changes:
            with self.subTest(field=name):
                with self.assertRaises(FrozenInstanceError):
                    setattr(detected, name, value)

    def test_detected_aroma_nested_objects_are_frozen(self):
        detected = self.detected()

        with self.assertRaises(FrozenInstanceError):
            detected.position.x = 100.0

        with self.assertRaises(FrozenInstanceError):
            detected.components.entries[0].intensity = 9.0

        with self.assertRaises(FrozenInstanceError):
            detected.raw_components.entries[0].intensity = 9.0

        with self.assertRaises(FrozenInstanceError):
            detected.recognition.recognized = True

    def test_detected_aroma_replacement_preserves_original(self):
        original = self.detected()
        original_distance = original.distance

        updated = replace(
            original,
            distance=original_distance + 1.0,
        )

        self.assertIsNot(updated, original)
        self.assertEqual(original.distance, original_distance)
        self.assertEqual(
            updated.distance,
            original_distance + 1.0,
        )

        self.assertIs(updated.position, original.position)
        self.assertIs(updated.components, original.components)
        self.assertIs(
            updated.raw_components,
            original.raw_components,
        )
        self.assertIs(
            updated.recognition,
            original.recognition,
        )

    def test_detected_aroma_rejects_mapping_state(self):
        original = self.detected()

        valid = dict(
            entity_id=original.entity_id,
            actual_identity=original.actual_identity,
            position=original.position,
            distance=original.distance,
            components=original.components,
            raw_components=original.raw_components,
            perceived_intensity=original.perceived_intensity,
            recognition=original.recognition,
        )

        invalid_values = (
            ("position", {"x": 2.0}),
            ("components", {"cat": 1.0}),
            ("raw_components", {"cat": 1.0}),
            ("recognition", {"recognized": False}),
        )

        for name, value in invalid_values:
            with self.subTest(field=name):
                kwargs = dict(valid)
                kwargs[name] = value

                with self.assertRaises(TypeError):
                    CatDetectedAroma(**kwargs)


if __name__ == "__main__":
    unittest.main()
