import unittest
from dataclasses import FrozenInstanceError

from core.entity.cronenberg import Cronenberg
from core.entity.cronenberg_system.chemical_marker import (
    CronenbergChemicalMarker
)


class CronenbergChemicalMarkerObjectStateTests(
    unittest.TestCase
):

    def _create_cronenberg(self):
        return Cronenberg(
            error=RuntimeError("chemical marker"),
            source_component="chemical_test",
            source_operation="aroma",
        )

    def _assert_object_only(self, value):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value["formula"]

    def test_marker_is_object_only_state(
        self
    ):
        marker = (
            self._create_cronenberg()
            .aroma_chemical_marker
        )

        self.assertIsInstance(
            marker,
            CronenbergChemicalMarker,
        )
        self._assert_object_only(marker)

    def test_marker_exposes_chemical_attributes(
        self
    ):
        marker = (
            self._create_cronenberg()
            .aroma_chemical_marker
        )

        self.assertEqual(
            marker.molecule,
            "ozone",
        )
        self.assertEqual(marker.formula, "O3")

    def test_marker_is_immutable(
        self
    ):
        marker = (
            self._create_cronenberg()
            .aroma_chemical_marker
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            marker.formula = "changed"


if __name__ == "__main__":
    unittest.main()
