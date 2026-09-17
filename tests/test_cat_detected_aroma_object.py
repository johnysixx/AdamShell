import unittest

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

        self.observer.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

        self.other.position = {
            "x": 2.0,
            "y": 0.0,
            "z": 0.0,
        }

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

    def test_chemical_component_maps_remain_dynamic_maps(
        self
    ):
        detected = self.detected()

        self.assertIsInstance(
            detected.components,
            dict,
        )

        self.assertIsInstance(
            detected.raw_components,
            dict,
        )

        self.assertIn(
            "cat",
            detected.components,
        )

        self.assertIn(
            "cat",
            detected.raw_components,
        )


if __name__ == "__main__":
    unittest.main()
