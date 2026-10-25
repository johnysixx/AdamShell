import unittest

from quantum.event_bus import (
    QuantumEvent,
    QuantumEventBus,
    QuantumEventPublicationResult,
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

        self.assertIsInstance(
            result,
            QuantumEventPublicationResult,
        )

        self.assertIs(
            result.event,
            event,
        )

        snapshot = result.to_dict()
        snapshot[
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

    def test_handler_receives_isolated_object_snapshot(
        self
    ):
        bus = QuantumEventBus()

        def handler(event):
            self.assertIsInstance(event, QuantumEvent)

            event.payload["nested"]["count"] = 99

            return event.payload["nested"]["count"]

        bus.subscribe("test_event", handler)

        result = bus.publish(
            "test_event",
            nested={"count": 1},
        )

        event = bus.event_history[-1]

        self.assertEqual(result.results, (99,))
        self.assertIs(result.event, event)
        self.assertEqual(
            event.payload["nested"]["count"],
            1,
        )

    def test_subscribers_receive_independent_events(
        self
    ):
        bus = QuantumEventBus()
        received = []
        original = {"count": 1}

        def first(event):
            received.append(event)
            event.payload["nested"]["count"] = 99
            return event.payload["nested"]["count"]

        def second(event):
            received.append(event)
            return event.payload["nested"]["count"]

        bus.subscribe("test_event", first)
        bus.subscribe("test_event", second)

        result = bus.publish(
            "test_event",
            nested=original,
        )

        self.assertEqual(result.subscriber_count, 2)
        self.assertEqual(result.results, (99, 1))
        self.assertEqual(original["count"], 1)

        self.assertIsInstance(received[0], QuantumEvent)
        self.assertIsInstance(received[1], QuantumEvent)

        self.assertIsNot(received[0], received[1])
        self.assertIsNot(received[0], result.event)
        self.assertIsNot(received[1], result.event)

        self.assertIs(
            result.event,
            bus.event_history[-1],
        )

        self.assertEqual(
            result.event.payload["nested"]["count"],
            1,
        )

        with self.assertRaises(TypeError):
            _ = received[0]["payload"]

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
