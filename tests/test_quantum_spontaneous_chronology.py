import unittest
from unittest.mock import patch

from core.entity.components import SpatialVector3
from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.quantum_box_disappearance_state import (
    QuantumBoxDisappearedEvent,
)
from universe.quantum_lifecycle_timeline import (
    UniverseQuantumLifecycleTimeline,
)
from universe.quantum_box_lifecycle_validator import (
    QuantumBoxLifecycleValidator,
)
from universe.universe import Universe


class QuantumSpontaneousChronologyTests(unittest.TestCase):

    def created(self, box_id="box", tick=0):
        return QuantumBoxCreatedEvent(
            box_id=box_id,
            position=SpatialVector3.zero(),
            layer="quantum_layer",
            tick=tick,
        )

    def collapsed(
        self,
        box_id="box",
        tick=0,
        cause="spontaneous",
    ):
        return QuantumBoxCollapsedEvent(
            quantum_box_id=box_id,
            result="empty",
            cause=cause,
            observer=None,
            tick=tick,
        )

    def disappeared(
        self,
        box_id="box",
        tick=0,
        cause="spontaneous",
    ):
        return QuantumBoxDisappearedEvent(
            box_id=box_id,
            cause=cause,
            tick=tick,
        )

    def test_spontaneous_collapse_at_tick_zero_rejected(self):
        history = (
            self.created(tick=0),
            self.collapsed(tick=0),
        )

        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(history)

    def test_spontaneous_collapse_on_creation_tick_rejected(self):
        history = (
            self.created(tick=2),
            self.collapsed(tick=2),
        )

        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(history)

    def test_spontaneous_collapse_on_later_tick_accepted(self):
        history = (
            self.created(tick=2),
            self.collapsed(tick=3),
            self.disappeared(tick=3),
        )

        result = QuantumBoxLifecycleValidator.validate(
            history
        )

        self.assertEqual(result, ())

    def test_opened_collapse_in_creation_tick_stays_valid(self):
        history = (
            self.created(tick=2),
            self.collapsed(tick=2, cause="opened"),
            self.disappeared(tick=2, cause="opened"),
        )

        result = QuantumBoxLifecycleValidator.validate(
            history
        )

        self.assertEqual(result, ())

    def test_reused_id_checks_most_recent_creation(self):
        history = (
            self.created(tick=0),
            self.collapsed(tick=1),
            self.disappeared(tick=1),
            self.created(tick=1),
            self.collapsed(tick=1),
        )

        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(history)

        valid = history[:-1] + (
            self.collapsed(tick=2),
        )

        remaining = QuantumBoxLifecycleValidator.validate(
            valid
        )

        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].created_tick, 1)
        self.assertEqual(remaining[0].collapse_tick, 2)

    def test_invalid_chronology_is_atomic_for_both_replayers(self):
        history = (
            self.created(tick=0),
            self.collapsed(tick=0),
        )

        for combined in (False, True):
            with self.subTest(combined=combined):
                target = Universe(
                    universe_id="invalid-spontaneous"
                )

                before = target.snapshot
                before_clock = target.quantum_state.to_dict()

                with self.assertRaises(ValueError):
                    if combined:
                        target.replay_quantum_history(
                            box_events=history,
                            clock_events=(),
                        )
                    else:
                        target.replay_quantum_box_history(
                            history
                        )

                self.assertEqual(target.snapshot, before)
                self.assertEqual(
                    target.quantum_state.to_dict(),
                    before_clock,
                )
                self.assertEqual(target.quantum_boxes, [])

    def test_real_spontaneous_history_remains_valid(self):
        source = Universe(universe_id="real-spontaneous")
        source.enable_quantum_layer()

        source.create_quantum_box(
            box_id="real_box",
        )
        source.should_collapse_quantum_box = (
            lambda _box: True
        )

        with patch(
            "core.entity.quantum_box.random.choice",
            return_value="empty",
        ):
            source.tick_quantum_unprotected()

        self.assertEqual(
            QuantumBoxLifecycleValidator.validate(
                source.quantum_events
            ),
            (),
        )

        timeline = source.quantum_lifecycle_timeline()

        self.assertEqual(
            [event.name for event in timeline],
            [
                "quantum_box_created",
                "universe_quantum_tick_advanced",
                "quantum_box_collapsed",
                "quantum_box_disappeared",
            ],
        )

        target = Universe(universe_id="real-spontaneous")
        target.enable_quantum_layer()

        result = target.replay_quantum_history(
            box_events=source.quantum_events,
            clock_events=source.quantum_clock_events,
        )

        self.assertEqual(result, ())
        self.assertEqual(target.quantum_state.tick_count, 1)


if __name__ == "__main__":
    unittest.main()
