from cats.cat_estrous_phase import CatEstrousPhase
from dataclasses import dataclass

from universe.logger import UniverseLogger


@dataclass(slots=True, frozen=True)
class CatEstrousCycleEvent:
    name: str
    cat: str
    day: int | None
    phase: CatEstrousPhase
    estrus_active: bool
    phase_changed: bool
    cycle_day: int | None = None
    reason: str | None = None

    def __post_init__(self):
        allowed_names = {
            "cat_estrous_cycle_advanced",
            "cat_estrus_ended_after_ovulation",
            "cat_estrus_started",
            "cat_interestrus_started",
            "cat_estrous_cycle_inactive",
        }

        if self.name not in allowed_names:
            raise ValueError(
                "Unsupported cat estrous cycle "
                "event name."
            )

        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )
        if not isinstance(
            self.phase,
            CatEstrousPhase,
        ):
            raise TypeError(
                "Cat estrous cycle event phase "
                "must be a CatEstrousPhase object."
            )
        object.__setattr__(
            self,
            "estrus_active",
            bool(self.estrus_active),
        )
        object.__setattr__(
            self,
            "phase_changed",
            bool(self.phase_changed),
        )

        if self.day is not None:
            object.__setattr__(
                self,
                "day",
                int(self.day),
            )

        if self.cycle_day is not None:
            object.__setattr__(
                self,
                "cycle_day",
                int(self.cycle_day),
            )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(self.reason),
            )

    def to_dict(self):
        snapshot = {
            "name": self.name,
            "cat": self.cat,
            "day": self.day,
            "phase": self.phase.value,
            "estrus_active": self.estrus_active,
            "phase_changed": self.phase_changed,
        }

        if self.cycle_day is not None:
            snapshot[
                "cycle_day"
            ] = self.cycle_day

        if self.reason is not None:
            snapshot[
                "reason"
            ] = self.reason

        return snapshot


class CatEstrousCycleResolver:

    DEFAULT_ESTRUS_DAYS = 7
    DEFAULT_INTERESTRUS_DAYS = 8

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def tick_day(
        self,
        cat,
        day=None
    ):
        reproduction = cat.reproduction

        if not self._can_cycle(
            cat
        ):
            return self._set_inactive(
                cat=cat,
                reason=self._inactive_reason(
                    cat
                ),
                day=day
            )

        phase = reproduction.estrous_phase

        if phase is CatEstrousPhase.INACTIVE:
            return self._start_estrus(
                cat=cat,
                day=day
            )

        reproduction.estrous_cycle_day = int(
            reproduction.estrous_cycle_day
        ) + 1

        if phase is CatEstrousPhase.ESTRUS:
            duration = int(
                reproduction.estrus_duration_days
            )

            if (
                reproduction.estrous_cycle_day
                >= duration
            ):
                return self._start_interestrus(
                    cat=cat,
                    day=day
                )

        elif phase is CatEstrousPhase.INTERESTRUS:
            duration = int(
                reproduction.interestrus_duration_days
            )

            if (
                reproduction.estrous_cycle_day
                >= duration
            ):
                return self._start_estrus(
                    cat=cat,
                    day=day
                )

        event = CatEstrousCycleEvent(
            name="cat_estrous_cycle_advanced",
            cat=cat.name,
            day=day,
            phase=phase,
            cycle_day=(
                reproduction.estrous_cycle_day
            ),
            estrus_active=(
                reproduction.estrus_active
            ),
            phase_changed=False,
        )

        self.record_event(
            event
        )

        return event

    def activate_estrus(
        self,
        cat,
        day=None
    ):
        if not self._can_cycle(
            cat
        ):
            return self._set_inactive(
                cat=cat,
                reason=self._inactive_reason(
                    cat
                ),
                day=day
            )

        return self._start_estrus(
            cat=cat,
            day=day
        )

    def end_estrus_after_ovulation(
        self,
        cat,
        day=None
    ):
        reproduction = cat.reproduction

        reproduction.estrous_phase = CatEstrousPhase.DIESTRUS

        reproduction.estrus_active = False

        reproduction.estrous_cycle_day = 0

        event = CatEstrousCycleEvent(
            name=(
                "cat_estrus_ended_after_ovulation"
            ),
            cat=cat.name,
            day=day,
            phase=CatEstrousPhase.DIESTRUS,
            estrus_active=False,
            phase_changed=True,
        )

        self.record_event(
            event
        )

        return event

    def _start_estrus(
        self,
        cat,
        day=None
    ):
        reproduction = cat.reproduction

        reproduction.estrous_phase = CatEstrousPhase.ESTRUS

        reproduction.estrus_active = True

        reproduction.estrous_cycle_day = 0

        event = CatEstrousCycleEvent(
            name="cat_estrus_started",
            cat=cat.name,
            day=day,
            phase=CatEstrousPhase.ESTRUS,
            cycle_day=0,
            estrus_active=True,
            phase_changed=True,
        )

        self.record_event(
            event
        )

        UniverseLogger.event(
            f"CAT ESTRUS STARTED: {cat.name}"
        )

        return event

    def _start_interestrus(
        self,
        cat,
        day=None
    ):
        reproduction = cat.reproduction

        reproduction.estrous_phase = CatEstrousPhase.INTERESTRUS

        reproduction.estrus_active = False

        reproduction.estrous_cycle_day = 0

        reproduction.mating_window_open = False

        reproduction.mating_contacts = []

        reproduction.potential_fathers = []

        reproduction.estrous_cycles_completed = int(
            reproduction.estrous_cycles_completed
        ) + 1

        event = CatEstrousCycleEvent(
            name="cat_interestrus_started",
            cat=cat.name,
            day=day,
            phase=CatEstrousPhase.INTERESTRUS,
            cycle_day=0,
            estrus_active=False,
            phase_changed=True,
        )

        self.record_event(
            event
        )

        return event

    def _set_inactive(
        self,
        cat,
        reason,
        day=None
    ):
        reproduction = cat.reproduction

        reproduction.estrous_phase = CatEstrousPhase.INACTIVE

        reproduction.estrus_active = False

        reproduction.estrous_cycle_day = 0

        event = CatEstrousCycleEvent(
            name="cat_estrous_cycle_inactive",
            cat=cat.name,
            day=day,
            phase=CatEstrousPhase.INACTIVE,
            estrus_active=False,
            reason=reason,
            phase_changed=False,
        )

        self.record_event(
            event
        )

        return event

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            CatEstrousCycleEvent,
        ):
            raise TypeError(
                "Estrous cycle history requires "
                "a CatEstrousCycleEvent object."
            )

        self.history.append(
            event
        )

        return event

    @staticmethod
    def _can_cycle(
        cat
    ):
        reproduction = cat.reproduction

        return (
            cat.sex == "female"
            and not reproduction.neutered
            and reproduction.fertile
            and not reproduction.pregnant
        )

    @staticmethod
    def _inactive_reason(
        cat
    ):
        reproduction = cat.reproduction

        if cat.sex != "female":
            return "not_female"

        if reproduction.neutered:
            return "neutered"

        if reproduction.pregnant:
            return "pregnant"

        if not reproduction.fertile:
            return "not_reproductively_mature"

        return "cycle_unavailable"
