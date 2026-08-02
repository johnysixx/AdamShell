from universe.logger import UniverseLogger


class LifeCycleSystem:

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.handlers = []
        self.history = []
        self.day = 0

    def register(
        self,
        handler
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
            False
        ):
            event = {
                "name": "life_cycle_tick_skipped",
                "reason": (
                    "physical_universe_not_started"
                ),
                "day": self.day,
                "processed_handlers": 0,
                "advanced": False
            }

            self.history.append(
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

            results.append(
                result
            )

        event = {
            "name": "life_cycle_day_completed",
            "day": self.day,
            "processed_handlers": len(
                results
            ),
            "results": results,
            "advanced": True
        }

        self.history.append(
            event
        )

        UniverseLogger.event(
            "LIFE CYCLE DAY="
            f"{self.day} "
            "HANDLERS="
            f"{len(results)}"
        )

        return event