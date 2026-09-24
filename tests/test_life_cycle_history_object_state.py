import unittest

from lifecycle.life_cycle_system import (
    LifeCycleDayCompletedEvent,
    LifeCycleSystem,
    LifeCycleTickSkippedEvent,
)


class FakeUniverse:

    def __init__(
        self,
        started,
    ):
        self.physical_universe_started = (
            started
        )


class FakeHandler:

    def tick_day(
        self,
        day,
    ):
        return {
            "day": day,
            "nested": [
                {
                    "value": 7,
                },
            ],
        }


class LifeCycleHistoryObjectStateTests(
    unittest.TestCase
):

    def test_skipped_history_uses_object_state(
        self
    ):
        system = LifeCycleSystem(
            FakeUniverse(
                started=False
            )
        )

        result = system.tick_day()

        event = (
            system.history[-1]
        )

        self.assertIsInstance(
            event,
            LifeCycleTickSkippedEvent,
        )

        self.assertFalse(
            event.advanced
        )

        self.assertEqual(
            result["day"],
            0,
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
            _ = event["day"]

    def test_completed_history_uses_object_state(
        self
    ):
        system = LifeCycleSystem(
            FakeUniverse(
                started=True
            )
        )

        system.register(
            FakeHandler()
        )

        result = system.tick_day()

        event = (
            system.history[-1]
        )

        self.assertIsInstance(
            event,
            LifeCycleDayCompletedEvent,
        )

        self.assertEqual(
            event.day,
            1,
        )

        self.assertEqual(
            event.processed_handlers,
            1,
        )

        self.assertEqual(
            result[
                "processed_handlers"
            ],
            1,
        )

    def test_result_snapshot_is_detached_from_history(
        self
    ):
        system = LifeCycleSystem(
            FakeUniverse(
                started=True
            )
        )

        system.register(
            FakeHandler()
        )

        result = system.tick_day()

        event = (
            system.history[-1]
        )

        result[
            "results"
        ][0][
            "nested"
        ][0][
            "value"
        ] = 99

        self.assertEqual(
            event.results[0][
                "nested"
            ][0][
                "value"
            ],
            7,
        )

        with self.assertRaises(
            TypeError
        ):
            event.results[0][
                "nested"
            ][0][
                "value"
            ] = 99

    def test_history_rejects_mapping_event(
        self
    ):
        system = LifeCycleSystem(
            FakeUniverse(
                started=True
            )
        )

        with self.assertRaises(TypeError):
            system.record_event(
                {
                    "name": (
                        "life_cycle_day_completed"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
