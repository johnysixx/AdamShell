from copy import deepcopy
from dataclasses import dataclass, field, fields, replace

from core.entity.quantum_box import QuantumBox
from universe.quantum_box_lifecycle_replayer import (
    QuantumBoxLifecycleReplayer,
)
from universe.quantum_lifecycle_timeline import (
    UniverseQuantumLifecycleTimeline,
)
from universe.quantum_clock_replayer import (
    UniverseQuantumClockReplayer,
)
from universe.quantum_state import UniverseQuantumState
from universe.universe_statistics import UniverseStatistics


@dataclass(slots=True)
class _QuantumHistoryReplayStage:
    """Isolated object state shared by both replay engines."""

    quantum_state: UniverseQuantumState
    quantum_boxes: list[QuantumBox] = field(
        default_factory=list,
    )
    statistics: UniverseStatistics = field(
        default_factory=UniverseStatistics,
    )


class UniverseQuantumHistoryReplayer:
    """Atomically restore box lifecycles and quantum clock."""

    @staticmethod
    def replay(
        universe,
        *,
        box_events,
        clock_events,
        preserve_history=False,
    ):
        try:
            box_events = tuple(box_events)
        except TypeError as error:
            raise TypeError(
                "Quantum box history must be iterable."
            ) from error

        try:
            clock_events = tuple(clock_events)
        except TypeError as error:
            raise TypeError(
                "Quantum clock history must be iterable."
            ) from error

        if type(preserve_history) is not bool:
            raise TypeError(
                "preserve_history must be bool."
            )

        if preserve_history and (
            universe.quantum_events
            or universe.quantum_clock_events
        ):
            raise ValueError(
                "Resumable replay requires empty "
                "target history streams."
            )

        statistics = universe.statistics

        if (
            universe.quantum_boxes
            or statistics.total_quantum_boxes_created
            or statistics.total_quantum_boxes_disappeared
            or statistics.total_quantum_collapses
        ):
            raise ValueError(
                "Combined quantum replay requires "
                "an empty target box lifecycle."
            )

        state = universe.quantum_state

        if not isinstance(state, UniverseQuantumState):
            raise TypeError(
                "Combined replay requires UniverseQuantumState."
            )

        # One shared validator for both histories.
        validated = UniverseQuantumLifecycleTimeline.validate(
            box_events=box_events,
            clock_events=clock_events,
        )
        active_boxes = validated.active_boxes

        # Work only with detached objects until both
        # replay engines have completed successfully.
        staged = _QuantumHistoryReplayStage(
            quantum_state=replace(state),
        )

        UniverseQuantumClockReplayer.replay(
            staged,
            clock_events,
        )

        # Cross-stream chronology was validated above.
        last_tick = staged.quantum_state.tick_count

        QuantumBoxLifecycleReplayer.replay(
            staged,
            box_events,
        )

        # Restore the ages of surviving boxes using
        # their most recent creation tick.
        for record in active_boxes:
            box = next(
                (
                    item
                    for item in staged.quantum_boxes
                    if item.id == record.box_id
                ),
                None,
            )

            if box is None:
                raise RuntimeError(
                    "Validated active quantum box missing "
                    "from staged replay."
                )

            box.age_ticks = (
                last_tick - record.created_tick
            )

        # Prepare detached historical records before
        # publishing any reconstructed runtime state.
        # A deepcopy failure must leave the target intact.
        if preserve_history:
            retained_box_events = deepcopy(box_events)
            retained_clock_events = deepcopy(clock_events)

        # Canonical registries must support in-place rollback.
        registries = (
            universe.quantum_boxes,
            universe.quantum_events,
            universe.quantum_clock_events,
        )

        if not all(
            isinstance(registry, list)
            for registry in registries
        ):
            raise TypeError(
                "Combined quantum replay requires list registries."
            )

        # Snapshot the existing canonical objects before
        # publishing any reconstructed state.
        boxes_before = tuple(universe.quantum_boxes)
        box_events_before = tuple(universe.quantum_events)
        clock_events_before = tuple(
            universe.quantum_clock_events
        )

        statistic_names = (
            "total_quantum_boxes_created",
            "total_quantum_collapses",
            "total_quantum_boxes_disappeared",
        )

        statistics_before = tuple(
            (name, getattr(statistics, name))
            for name in statistic_names
        )

        clock_before = tuple(
            (item.name, getattr(state, item.name))
            for item in fields(UniverseQuantumState)
        )

        try:
            # Publish into the original canonical objects.
            universe.quantum_boxes.extend(
                staged.quantum_boxes
            )

            for name in statistic_names:
                setattr(
                    statistics,
                    name,
                    getattr(staged.statistics, name),
                )

            for item in fields(UniverseQuantumState):
                setattr(
                    state,
                    item.name,
                    getattr(
                        staged.quantum_state,
                        item.name,
                    ),
                )

            if preserve_history:
                universe.quantum_events.extend(
                    retained_box_events
                )
                universe.quantum_clock_events.extend(
                    retained_clock_events
                )

        except BaseException:
            # A publication hook may append or assign
            # successfully and then raise. Restore the
            # original containers without invoking their
            # potentially faulty overridden methods.
            list.__setitem__(
                universe.quantum_boxes,
                slice(None),
                boxes_before,
            )

            list.__setitem__(
                universe.quantum_events,
                slice(None),
                box_events_before,
            )

            list.__setitem__(
                universe.quantum_clock_events,
                slice(None),
                clock_events_before,
            )

            # Bypass injected __setattr__ failures while
            # preserving the original object identities.
            for name, value in statistics_before:
                object.__setattr__(
                    statistics,
                    name,
                    value,
                )

            for name, value in clock_before:
                object.__setattr__(
                    state,
                    name,
                    value,
                )

            raise

        return tuple(universe.quantum_boxes)
