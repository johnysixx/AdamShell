from dataclasses import (
    FrozenInstanceError,
    dataclass,
)
import unittest

from lifecycle.life_cycle_result_state import (
    LifeCycleDayCompletedEvent,
    LifeCycleTickSkippedEvent,
)
from lifecycle.life_cycle_system import (
    LifeCycleSystem,
)


class FakeUniverse:

    def __init__(
        self,
        started,
    ):
        self.physical_universe_started = (
            started
        )


@dataclass(slots=True, frozen=True)
class FakeLifeCycleResult:

    day: int
    value: int = 7


class FakeHandler:

    def tick_day(
        self,
        day,
    ):
        return FakeLifeCycleResult(
            day=day
        )


class LegacyMappingHandler:

    def tick_day(
        self,
        day,
    ):
        return {
            "day": day,
        }


class LifeCycleHistoryObjectStateTests(
    unittest.TestCase
):

    def assert_object_only(
        self,
        value,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value[
                "name"
            ]

    def test_skipped_result_and_history_use_object_state(
        self
    ):
        system = LifeCycleSystem(
            FakeUniverse(
                started=False
            )
        )

        result = system.tick_day()

        stored = (
            system.history[-1]
        )

        self.assertIsInstance(
            result,
            LifeCycleTickSkippedEvent,
        )

        self.assertIsInstance(
            stored,
            LifeCycleTickSkippedEvent,
        )

        self.assertFalse(
            result.advanced
        )

        self.assertEqual(
            result.reason,
            "physical_universe_not_started",
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            result
        )

        self.assert_object_only(
            stored
        )

    def test_completed_result_and_history_use_object_state(
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

        stored = (
            system.history[-1]
        )

        self.assertIsInstance(
            result,
            LifeCycleDayCompletedEvent,
        )

        self.assertIsInstance(
            stored,
            LifeCycleDayCompletedEvent,
        )

        self.assertEqual(
            result.day,
            1,
        )

        self.assertEqual(
            result.processed_handlers,
            1,
        )

        self.assertIsInstance(
            result.results,
            tuple,
        )

        self.assertIsInstance(
            result.results[0],
            FakeLifeCycleResult,
        )

        self.assertEqual(
            result.results[0].value,
            7,
        )

        self.assertEqual(
            stored,
            result,
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assert_object_only(
            result
        )

    def test_completed_wrapper_shares_only_immutable_child_object(
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

        stored = (
            system.history[-1]
        )

        self.assertIsNot(
            stored,
            result,
        )

        self.assertIs(
            stored.results[0],
            result.results[0],
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.results[0].value = 99

    def test_mapping_handler_result_is_rejected(
        self
    ):
        system = LifeCycleSystem(
            FakeUniverse(
                started=True
            )
        )

        system.register(
            LegacyMappingHandler()
        )

        with self.assertRaises(
            TypeError
        ):
            system.tick_day()

    def test_history_rejects_mapping_event(
        self
    ):
        system = LifeCycleSystem(
            FakeUniverse(
                started=True
            )
        )

        with self.assertRaises(
            TypeError
        ):
            system.record_event(
                {
                    "name":
                        "life_cycle_day_completed",
                }
            )


if __name__ == "__main__":
    unittest.main()
