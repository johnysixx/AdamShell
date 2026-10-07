from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class LifeCycleTickSkippedEvent:

    day: int

    reason: str = field(
        default="physical_universe_not_started",
        init=False,
    )

    name: str = field(
        default="life_cycle_tick_skipped",
        init=False,
    )

    processed_handlers: int = field(
        default=0,
        init=False,
    )

    advanced: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "day",
            int(self.day),
        )


@dataclass(slots=True, frozen=True)
class LifeCycleDayCompletedEvent:

    day: int
    results: tuple[object, ...]

    name: str = field(
        default="life_cycle_day_completed",
        init=False,
    )

    advanced: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "day",
            int(self.day),
        )

        results = tuple(
            self.results
        )

        if any(
            isinstance(
                result,
                dict,
            )
            for result
            in results
        ):
            raise TypeError(
                "Life cycle handler results "
                "must be objects, not mappings."
            )

        object.__setattr__(
            self,
            "results",
            results,
        )

    @property
    def processed_handlers(self):
        return len(
            self.results
        )
