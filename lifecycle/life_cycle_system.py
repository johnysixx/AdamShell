from dataclasses import dataclass, field
from types import MappingProxyType

from universe.logger import UniverseLogger


class _FrozenLifeCycleList(tuple):
    pass


class _FrozenLifeCycleSet(frozenset):
    pass


def _freeze_life_cycle_payload(value):
    if isinstance(value, dict):
        return MappingProxyType({
            key: _freeze_life_cycle_payload(item)
            for key, item in value.items()
        })

    if isinstance(value, list):
        return _FrozenLifeCycleList(
            _freeze_life_cycle_payload(item)
            for item in value
        )

    if isinstance(value, tuple):
        return tuple(
            _freeze_life_cycle_payload(item)
            for item in value
        )

    if isinstance(value, set):
        return _FrozenLifeCycleSet(
            _freeze_life_cycle_payload(item)
            for item in value
        )

    if isinstance(value, frozenset):
        return frozenset(
            _freeze_life_cycle_payload(item)
            for item in value
        )

    return value


def _thaw_life_cycle_payload(value):
    if isinstance(
        value,
        MappingProxyType,
    ):
        return {
            key: _thaw_life_cycle_payload(item)
            for key, item in value.items()
        }

    if isinstance(
        value,
        _FrozenLifeCycleList,
    ):
        return [
            _thaw_life_cycle_payload(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return tuple(
            _thaw_life_cycle_payload(item)
            for item in value
        )

    if isinstance(
        value,
        _FrozenLifeCycleSet,
    ):
        return {
            _thaw_life_cycle_payload(item)
            for item in value
        }

    if isinstance(value, frozenset):
        return frozenset(
            _thaw_life_cycle_payload(item)
            for item in value
        )

    return value


@dataclass(slots=True, frozen=True)
class LifeCycleTickSkippedEvent:

    day: int
    reason: str = field(
        default=(
            "physical_universe_not_started"
        ),
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

    def to_dict(self):
        return {
            "name": self.name,
            "reason": self.reason,
            "day": self.day,
            "processed_handlers": (
                self.processed_handlers
            ),
            "advanced": self.advanced,
        }


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

        object.__setattr__(
            self,
            "results",
            tuple(
                _freeze_life_cycle_payload(
                    result
                )
                for result
                in self.results
            ),
        )

    @property
    def processed_handlers(self):
        return len(
            self.results
        )

    def to_dict(self):
        return {
            "name": self.name,
            "day": self.day,
            "processed_handlers": (
                self.processed_handlers
            ),
            "results": [
                _thaw_life_cycle_payload(
                    result
                )
                for result
                in self.results
            ],
            "advanced": self.advanced,
        }


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
            event = LifeCycleTickSkippedEvent(
                day=self.day,
            )

            self.record_event(
                event
            )

            return event.to_dict()

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

        event = LifeCycleDayCompletedEvent(
            day=self.day,
            results=tuple(
                results
            ),
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

        return event.to_dict()

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
            event
        )

        return event
