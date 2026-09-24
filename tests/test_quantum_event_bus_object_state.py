import unittest

from quantum.event_bus import (
    QuantumEvent,
    QuantumEventBus,
)


class QuantumEventBusObjectStateTests(
    unittest.TestCase
):

    def test_event_history_uses_object_state(
        self
    ):
        bus = QuantumEventBus()

        result = bus.publish(
            "test_event",
            value=7,
            nested={
                "count": 1,
            },
        )

        event = (
            bus.event_history[-1]
        )

        self.assertIsInstance(
            event,
            QuantumEvent,
        )

        self.assertEqual(
            event.name,
            "test_event",
        )

        self.assertEqual(
            event.payload["value"],
            7,
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
            _ = event["name"]

        with self.assertRaises(TypeError):
            event.payload[
                "value"
            ] = 99

        result[
            "event"
        ][
            "payload"
        ][
            "nested"
        ][
            "count"
        ] = 99

        self.assertEqual(
            event.payload[
                "nested"
            ][
                "count"
            ],
            1,
        )

    def test_handler_receives_boundary_snapshot(
        self
    ):
        bus = QuantumEventBus()

        def handler(event):
            event[
                "payload"
            ][
                "value"
            ] = 99

            return event[
                "payload"
            ][
                "value"
            ]

        bus.subscribe(
            "test_event",
            handler,
        )

        result = bus.publish(
            "test_event",
            value=7,
        )

        event = (
            bus.event_history[-1]
        )

        self.assertEqual(
            result["results"],
            [99],
        )

        self.assertEqual(
            result[
                "event"
            ][
                "payload"
            ][
                "value"
            ],
            99,
        )

        self.assertEqual(
            event.payload["value"],
            7,
        )

    def test_history_rejects_mapping_event(
        self
    ):
        bus = QuantumEventBus()

        with self.assertRaises(TypeError):
            bus.record_event(
                {
                    "name": "legacy_mapping",
                    "payload": {},
                }
            )


if __name__ == "__main__":
    unittest.main()
