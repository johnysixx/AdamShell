from core.entity.components import SpatialVector3
import unittest
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



if __name__ == "__main__":
    unittest.main()
