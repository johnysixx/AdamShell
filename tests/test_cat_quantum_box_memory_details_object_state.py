import unittest

from cats.cat_quantum_box_memory_details import (
    CatQuantumBoxObservedMemoryDetails,
    CatQuantumBoxTransferFailedMemoryDetails,
    CatQuantumBoxTransferMemoryDetails,
)
from cats.memory import CatMemory
from core.entity.components import (
    SpatialVector3,
)


class CatQuantumBoxMemoryDetailsObjectStateTests(
    unittest.TestCase
):

    def assert_object_only(
        self,
        value,
    ):
        for name in (
            "get",
            "keys",
            "items",
            "values",
            "update",
            "__getitem__",
            "__setitem__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    name,
                )
            )

    def test_observation_details_are_object_only(
        self
    ):
        details = (
            CatQuantumBoxObservedMemoryDetails(
                box_id="box_1",
                position=SpatialVector3.zero(),
            )
        )

        self.assert_object_only(
            details
        )

        self.assertEqual(
            details.box_id,
            "box_1",
        )

    def test_transfer_details_are_object_only(
        self
    ):
        details = (
            CatQuantumBoxTransferMemoryDetails(
                source_layer=
                    "quantum_layer",
                target_layer=
                    "meeting_place",
                target_box_consumed=True,
                energy_j=1.0,
                trail_id="trail_1",
            )
        )

        self.assert_object_only(
            details
        )

        self.assertTrue(
            details.target_box_consumed
        )

    def test_failure_details_are_object_only(
        self
    ):
        details = (
            CatQuantumBoxTransferFailedMemoryDetails(
                reason="test_failure",
                source_layer=
                    "quantum_layer",
                target_layer=
                    "meeting_place",
                cronenberg_id=
                    "cronenberg_1",
            )
        )

        self.assert_object_only(
            details
        )

        self.assertEqual(
            details.reason,
            "test_failure",
        )

    def test_memory_keeps_quantum_box_details_object(
        self
    ):
        memory = CatMemory(
            "quantum_memory_cat"
        )

        details = (
            CatQuantumBoxTransferMemoryDetails(
                source_layer=
                    "quantum_layer",
                target_layer=
                    "meeting_place",
                target_box_consumed=True,
                energy_j=1.0,
                trail_id="trail_1",
            )
        )

        returned = memory.remember(
            event_type=(
                "quantum_box_layer_transfer"
            ),
            location=(
                SpatialVector3.zero()
            ),
            details=details,
        )

        stored = (
            memory.records()[0]
        )

        self.assertIsInstance(
            returned.details,
            CatQuantumBoxTransferMemoryDetails,
        )

        self.assertIsInstance(
            stored.details,
            CatQuantumBoxTransferMemoryDetails,
        )

        self.assertIsInstance(
            stored.location,
            SpatialVector3,
        )

        self.assertEqual(
            stored.details.source_layer,
            "quantum_layer",
        )

        self.assertEqual(
            stored.details.target_layer,
            "meeting_place",
        )

        self.assertFalse(
            hasattr(
                memory,
                "public_state",
            )
        )


if __name__ == "__main__":
    unittest.main()
