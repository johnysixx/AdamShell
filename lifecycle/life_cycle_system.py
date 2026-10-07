from dataclasses import replace

from lifecycle.life_cycle_result_state import (
    LifeCycleDayCompletedEvent,
    LifeCycleTickSkippedEvent,
)
from universe.logger import UniverseLogger


class LifeCycleSystem:

    def __init__(
        self,
        universe,
    ):
        self.universe = universe
        self.handlers = []
        self.history = []
        self.day = 0

    def register(
        self,
        handler,
    ):
        if handler in self.handlers:
            return False

        self.handlers.append(
            handler
        )

        return True

    def tick_day(self):
        if not getattr(
            self.universe,
            "physical_universe_started",
            False,
        ):
            event = (
                LifeCycleTickSkippedEvent(
                    day=self.day,
                )
            )

            self.record_event(
                event
            )

            return event

        self.day += 1

        results = []

        for handler in list(
            self.handlers
        ):
            result = handler.tick_day(
                day=self.day
            )

            if isinstance(
                result,
                dict,
            ):
                raise TypeError(
                    "Life cycle handlers must "
                    "return result objects."
                )

            results.append(
                result
            )

        event = (
            LifeCycleDayCompletedEvent(
                day=self.day,
                results=tuple(
                    results
                ),
            )
        )

        self.record_event(
            event
        )

        UniverseLogger.event(
            "LIFE CYCLE DAY="
            f"{self.day} "
            "HANDLERS="
            f"{len(results)}"
        )

        return event

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                LifeCycleTickSkippedEvent,
                LifeCycleDayCompletedEvent,
            ),
        ):
            raise TypeError(
                "Life cycle history requires "
                "a life cycle event object."
            )

        self.history.append(
            replace(
                event
            )
        )

        return event
