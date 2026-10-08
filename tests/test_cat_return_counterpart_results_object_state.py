import unittest

from cats.cats import Cats
from core.entity.components import SpatialVector3
from core.entity.quantum_box_pairing_result_state import (
    QuantumBoxesPairedEvent,
)
from quantum.cat_return_counterpart_result_state import (
    CatReturnCounterpartCreatedEvent,
    CatReturnCounterpartCreatedResult,
    CatReturnCounterpartCreationFailedResult,
)
from universe.dark_sector import (
    QUANTUM_BOX_ENERGY_COST_J,
)
from universe.universe import Universe


class CatReturnCounterpartResultsObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="return_counterpart_cat",
            color="black",
            fur_length="short",
        )

        self.cat.current_layer = (
            "quantum_layer"
        )

        self.cat.position = SpatialVector3(
            x=4.0,
            y=1.0,
            z=0.0,
        )

        self.cat.idea_energy = (
            QUANTUM_BOX_ENERGY_COST_J
            * 4.0
        )

        self.source = (
            self.universe
            .create_quantum_box(
                layer="meeting_place"
            )
        )

    def assert_object_only(
        self,
        value,
    ):
        for method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value["name"]

    def test_quantum_box_pairing_event_is_object(
        self
    ):
        target = (
            self.universe
            .create_quantum_box(
                layer="quantum_layer"
            )
        )

        result = (
            self.source
            .pair_with(
                target
            )
        )

        self.assertIsInstance(
            result,
            QuantumBoxesPairedEvent,
        )

        self.assertTrue(
            result.paired
        )

        self.assert_object_only(
            result
        )

    def test_return_counterpart_result_is_object(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .create_return_counterpart(
                cat=self.cat,
                source_box_id=
                    self.source.id,
            )
        )

        self.assertIsInstance(
            result,
            CatReturnCounterpartCreatedResult,
        )

        self.assertTrue(
            result.created
        )

        self.assertIsInstance(
            result.position,
            SpatialVector3,
        )

        self.assertIsInstance(
            result.pair_event,
            QuantumBoxesPairedEvent,
        )

        self.assertEqual(
            result.counterpart.position,
            self.cat.position,
        )

        self.assert_object_only(
            result
        )

    def test_missing_source_failure_is_object(
        self
    ):
        result = (
            self.universe
            .cat_box_transfer
            .create_return_counterpart(
                cat=self.cat,
                source_box_id=
                    "missing_box",
            )
        )

        self.assertIsInstance(
            result,
            CatReturnCounterpartCreationFailedResult,
        )

        self.assertFalse(
            result.created
        )

        self.assertEqual(
            result.reason,
            "source_box_not_found",
        )

        self.assert_object_only(
            result
        )

    def test_insufficient_energy_failure_is_object(
        self
    ):
        self.cat.idea_energy = 0.0

        result = (
            self.universe
            .cat_box_transfer
            .create_return_counterpart(
                cat=self.cat,
                source_box_id=
                    self.source.id,
            )
        )

        self.assertIsInstance(
            result,
            CatReturnCounterpartCreationFailedResult,
        )

        self.assertEqual(
            result.reason,
            "insufficient_cat_energy",
        )

        self.assert_object_only(
            result
        )

    def test_history_stores_counterpart_event_object(
        self
    ):
        self.universe.cat_box_transfer            .create_return_counterpart(
                cat=self.cat,
                source_box_id=
                    self.source.id,
            )

        event = next(
            event
            for event
            in reversed(
                self.universe
                .cat_box_transfer
                .history
            )
            if isinstance(
                event,
                CatReturnCounterpartCreatedEvent,
            )
        )

        self.assertIsInstance(
            event.pair_event,
            QuantumBoxesPairedEvent,
        )

        self.assert_object_only(
            event
        )


if __name__ == "__main__":
    unittest.main()
