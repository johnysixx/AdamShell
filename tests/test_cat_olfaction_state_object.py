from core.entity.components import SpatialVector3
import unittest
from dataclasses import FrozenInstanceError, replace

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_olfaction import CatOlfaction
from cats.cat_olfaction_state import (
    CatOlfactionState,
)
from cats.cat_perception import CatPerception


class CatOlfactionStateObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="observer",
            color="black",
            fur_length="short",
        )

        self.cat.position = SpatialVector3(x=0.0, y=0.0, z=0.0)

    def test_sniff_returns_clean_object_state(
        self
    ):
        result = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        self.assertIsInstance(
            result,
            CatOlfactionState,
        )

        self.assertFalse(
            hasattr(
                result,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                result,
                "__getitem__",
            )
        )

        self.assertTrue(
            result.sniffed
        )

        self.assertEqual(
            result.cat,
            self.cat.name,
        )

    def test_detected_count_is_derived_from_aromas(
        self
    ):
        result = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        self.assertIsInstance(
            result.detected_aromas,
            tuple,
        )

        self.assertEqual(
            result.detected_count,
            len(result.detected_aromas),
        )

        with self.assertRaises(AttributeError):
            result.detected_aromas.append(object())

        self.assertEqual(
            result.detected_count,
            len(result.detected_aromas),
        )

    def test_perception_keeps_olfaction_object(
        self
    ):
        observations = CatPerception(
            self.cats
        ).observe(
            self.cat
        )

        self.assertIsInstance(
            observations.olfaction,
            CatOlfactionState,
        )



    def test_olfaction_snapshot_is_frozen(self):
        result = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        changes = (
            ("cat", "other"),
            ("radius", 100.0),
            ("detected_aromas", ()),
            ("ambient_aroma", None),
            ("ozone_detected", True),
            ("sniffed", False),
        )

        for name, value in changes:
            with self.subTest(field=name):
                with self.assertRaises(FrozenInstanceError):
                    setattr(result, name, value)

    def test_snapshot_rejects_invalid_runtime_records(self):
        invalid_values = (
            [],
            [object()],
            (object(),),
            ({"entity_id": "legacy"},),
        )

        for value in invalid_values:
            with self.subTest(value=repr(value)):
                with self.assertRaises(TypeError):
                    CatOlfactionState(
                        detected_aromas=value,
                    )

        with self.assertRaises(TypeError):
            CatOlfactionState(
                ambient_aroma={"source": "legacy"},
            )

        self.assertEqual(
            CatOlfactionState().detected_aromas,
            (),
        )

    def test_new_sniff_preserves_previous_snapshot(self):
        first = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        previous = first.detected_aromas
        previous_count = first.detected_count

        source = self.cats.create_cat(
            name="new_aroma_source",
            color="black",
            fur_length="short",
        )

        source.position = SpatialVector3(
            x=2.0, y=0.0, z=0.0
        )

        self.universe.entities.append(source)

        second = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        self.assertIs(first.detected_aromas, previous)
        self.assertEqual(first.detected_count, previous_count)

        self.assertTrue(
            any(
                item.actual_identity == "cat:new_aroma_source"
                for item in second.detected_aromas
            )
        )

        self.assertFalse(
            any(
                item.actual_identity == "cat:new_aroma_source"
                for item in first.detected_aromas
            )
        )

    def test_sniff_preserves_intensity_sort_order(self):
        for name, distance in (
            ("far_source", 6.0),
            ("near_source", 1.0),
        ):
            source = self.cats.create_cat(
                name=name,
                color="black",
                fur_length="short",
            )

            source.position = SpatialVector3(
                x=distance, y=0.0, z=0.0
            )

            self.universe.entities.append(source)

        result = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        self.assertIsInstance(result.detected_aromas, tuple)

        self.assertEqual(
            tuple(
                sorted(
                    result.detected_aromas,
                    key=lambda item: item.perceived_intensity,
                    reverse=True,
                )
            ),
            result.detected_aromas,
        )

        selected = [
            item
            for item in result.detected_aromas
            if item.actual_identity in (
                "cat:near_source",
                "cat:far_source",
            )
        ]

        self.assertEqual(
            [item.actual_identity for item in selected],
            ["cat:near_source", "cat:far_source"],
        )

        self.assertGreater(
            selected[0].perceived_intensity,
            selected[1].perceived_intensity,
        )


if __name__ == "__main__":
    unittest.main()
