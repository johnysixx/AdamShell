import unittest

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)
from universe.universe import Universe


class CronenbergManifestationEventObjectStateTests(
    unittest.TestCase
):

    def test_quantum_error_manifestation_stores_event_object(
        self,
    ):
        universe = Universe()

        cronenberg = (
            universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "manifestation test",
                ),
                source_component=(
                    "manifestation_test"
                ),
                source_operation=(
                    "create_cronenberg"
                ),
            )
        )

        event = universe.quantum_events[-1]

        self.assertIsInstance(
            event,
            CronenbergManifestedEvent,
        )

        self.assertEqual(
            event.cronenberg_id,
            cronenberg.id,
        )

        self.assertEqual(
            event.source_component,
            "manifestation_test",
        )

        self.assertEqual(
            event.source_operation,
            "create_cronenberg",
        )

        self.assertEqual(
            event.error_type,
            "RuntimeError",
        )

        self.assertEqual(
            event.error_message,
            "manifestation test",
        )

        self.assertEqual(
            event.quantum_tick,
            universe.quantum_state.tick_count,
        )

    def test_event_has_no_mapping_api(
        self,
    ):
        event = CronenbergManifestedEvent(
            cronenberg_id="cronenberg_1",
            source_component="test",
            source_operation="operation",
            error_type="RuntimeError",
            error_message="boom",
            quantum_tick=7,
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event[
                "cronenberg_id"
            ]

    def test_boundary_snapshot_is_detached(
        self,
    ):
        event = CronenbergManifestedEvent(
            cronenberg_id="cronenberg_1",
            source_component="test",
            source_operation="operation",
            error_type="RuntimeError",
            error_message="boom",
            quantum_tick=7,
        )

        boundary = event.to_dict()

        boundary[
            "source_component"
        ] = "changed"

        self.assertEqual(
            event.source_component,
            "test",
        )


if __name__ == "__main__":
    unittest.main()
