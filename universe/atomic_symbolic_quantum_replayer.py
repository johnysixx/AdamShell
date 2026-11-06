from copy import copy
from dataclasses import dataclass, field, fields, replace

from core.word.chronicle import Chronicle
from core.word.word import Word
from universe.quantum_history_replayer import (
    UniverseQuantumHistoryReplayer,
)
from universe.quantum_state import UniverseQuantumState
from universe.universe_statistics import UniverseStatistics


_SYMBOLIC_FIELDS = (
    "light",
    "space",
    "chaos",
    "order",
    "deep",
    "rules_modified",
)

_QUANTUM_STATISTICS = (
    "total_quantum_boxes_created",
    "total_quantum_collapses",
    "total_quantum_boxes_disappeared",
)


class _SymbolicReplayStage:
    """Replay words without mutating the target Universe."""

    def __init__(self, universe):
        # Reuse the canonical Universe.hear implementation
        # without constructing another Universe.
        self._hear = type(universe).hear

        for name in _SYMBOLIC_FIELDS:
            if hasattr(universe, name):
                setattr(
                    self,
                    name,
                    getattr(universe, name),
                )

    def hear(self, word):
        self._hear(self, word)


@dataclass(slots=True)
class _AtomicQuantumStage:
    quantum_state: UniverseQuantumState
    statistics: UniverseStatistics
    quantum_boxes: list = field(default_factory=list)
    quantum_events: list = field(default_factory=list)
    quantum_clock_events: list = field(default_factory=list)


class AtomicSymbolicQuantumReplayer:
    """
    Atomically prepare symbolic and quantum runtime replay.

    Runtime state is published only after both staged
    reconstructions succeed. Global logging is outside
    this transaction boundary.
    """

    @staticmethod
    def replay(
        universe,
        *,
        chronicle,
        box_events,
        clock_events,
        preserve_history=True,
    ):
        if not isinstance(chronicle, Chronicle):
            raise TypeError(
                "Combined replay requires Chronicle."
            )

        if type(preserve_history) is not bool:
            raise TypeError(
                "preserve_history must be bool."
            )

        if not isinstance(
            universe.quantum_state,
            UniverseQuantumState,
        ):
            raise TypeError(
                "Combined replay requires UniverseQuantumState."
            )

        if not isinstance(
            universe.statistics,
            UniverseStatistics,
        ):
            raise TypeError(
                "Combined replay requires UniverseStatistics."
            )

        # Freeze and validate the symbolic input before
        # executing either part of the transaction.
        words = tuple(chronicle.all())

        if not all(
            isinstance(word, Word)
            for word in words
        ):
            raise TypeError(
                "Combined replay requires Word objects."
            )

        # Stage the canonical symbolic semantics.
        symbolic = _SymbolicReplayStage(universe)

        for word in words:
            symbolic.hear(word)

        # Stage quantum replay using detached object state.
        # The existing quantum replayer performs validation,
        # age reconstruction and optional history copying.
        quantum = _AtomicQuantumStage(
            quantum_state=replace(
                universe.quantum_state
            ),
            statistics=copy(
                universe.statistics
            ),
        )

        UniverseQuantumHistoryReplayer.replay(
            quantum,
            box_events=box_events,
            clock_events=clock_events,
            preserve_history=preserve_history,
        )

        # All validation and reconstruction succeeded.
        # Publish into existing canonical runtime objects.
        universe.quantum_boxes.extend(
            quantum.quantum_boxes
        )

        for name in _QUANTUM_STATISTICS:
            setattr(
                universe.statistics,
                name,
                getattr(quantum.statistics, name),
            )

        for item in fields(UniverseQuantumState):
            setattr(
                universe.quantum_state,
                item.name,
                getattr(
                    quantum.quantum_state,
                    item.name,
                ),
            )

        if preserve_history:
            universe.quantum_events.extend(
                quantum.quantum_events
            )
            universe.quantum_clock_events.extend(
                quantum.quantum_clock_events
            )

        for name in _SYMBOLIC_FIELDS:
            if hasattr(symbolic, name):
                setattr(
                    universe,
                    name,
                    getattr(symbolic, name),
                )

        return tuple(universe.quantum_boxes)
