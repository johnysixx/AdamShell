import unittest

from cats.cat_quantum_box_origin_state import (
    CatQuantumBoxOriginState,
)
from core.entity.components import SpatialVector3
from universe.manifestation_result_state import (
    CatManifestationResult,
    CatManifestedEvent,
    EmptyQuantumBoxOpenedEvent,
)
from universe.universe import Universe


class UniverseManifestationResultObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(self, value, key):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_manifest_cat_returns_object_result_and_event(self):
        universe = Universe()
        universe.enable_quantum_layer()
        position = SpatialVector3(
            x=1.0,
            y=2.0,
            z=3.0,
        )

        result = universe.manifest_cat(
            name="manifested_object_cat",
            source="test",
            position=position,
        )

        self.assertIsInstance(
            result,
            CatManifestationResult,
        )
        self.assertIsInstance(
            result.event,
            CatManifestedEvent,
        )
        self.assertIs(
            universe.quantum_events[-1],
            result.event,
        )
        self.assertIs(
            result.event.position,
            position,
        )
        self.assertEqual(
            result.event.cat_name,
            result.cat.name,
        )
        self._assert_object_only(
            result,
            "cat",
        )
        self._assert_object_only(
            result.event,
            "name",
        )

    def test_quantum_box_cat_origin_is_object_state(self):
        universe = Universe()
        universe.enable_quantum_layer()

        result = universe.manifest_cat(
            name="box_origin_cat",
            source="quantum_box_opened",
        )

        origin = result.cat.quantum_box_origin

        self.assertIsInstance(
            origin,
            CatQuantumBoxOriginState,
        )
        self.assertTrue(origin.manifested_from_box)
        self.assertTrue(origin.born_in_quantum_layer)
        self.assertEqual(
            origin.source,
            "quantum_box_opened",
        )
        self._assert_object_only(
            origin,
            "source",
        )

    def test_open_quantum_box_cat_returns_manifested_event_object(self):
        universe = Universe()
        universe.enable_quantum_layer()
        box = universe.create_quantum_box()
        box.collapse_state = lambda **kwargs: "cat"
        observer = object()

        event = universe.open_quantum_box(
            box.id,
            observer=observer,
        )

        self.assertIsInstance(
            event,
            CatManifestedEvent,
        )
        self.assertEqual(
            event.collapse_cause,
            "opened",
        )
        self.assertEqual(event.box_id, box.id)
        self.assertIs(event.observer, observer)
        self.assertIs(
            universe.quantum_events[-1],
            event,
        )

    def test_spontaneous_quantum_box_cat_records_manifested_event_object(self):
        universe = Universe()
        universe.enable_quantum_layer()
        box = universe.create_quantum_box()
        box.collapse_state = lambda **kwargs: "cat"
        universe.should_collapse_quantum_box = (
            lambda current_box: True
        )

        universe.tick_quantum_unprotected()

        event = universe.quantum_events[-1]

        self.assertIsInstance(
            event,
            CatManifestedEvent,
        )
        self.assertEqual(
            event.collapse_cause,
            "spontaneous",
        )
        self.assertEqual(event.box_id, box.id)
        self.assertIsNone(event.observer)

    def test_open_empty_quantum_box_returns_object_event(self):
        universe = Universe()
        universe.enable_quantum_layer()
        box = universe.create_quantum_box()
        box.collapse_state = lambda **kwargs: "empty"

        event = universe.open_quantum_box(
            box.id,
            observer="observer",
        )

        self.assertIsInstance(
            event,
            EmptyQuantumBoxOpenedEvent,
        )
        self.assertEqual(event.box_id, box.id)
        self.assertEqual(event.observer, "observer")
        self._assert_object_only(
            event,
            "box_id",
        )


if __name__ == "__main__":
    unittest.main()
