import unittest

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
from universe.quantum_box_lifecycle_validator import (
    QuantumBoxLifecycleValidator,
)
from universe.universe import Universe


class QuantumBoxLifecycleValidatorTests(unittest.TestCase):

    def created(self, box_id="box", tick=0):
        return QuantumBoxCreatedEvent(
            box_id=box_id,
            position=SpatialVector3(
                x=0.0, y=0.0, z=0.0,
            ),
            layer="quantum_layer",
            tick=tick,
        )

    def collapsed(
        self,
        box_id="box",
        tick=0,
        cause="opened",
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
        cause="opened",
    ):
        return QuantumBoxDisappearedEvent(
            box_id=box_id,
            cause=cause,
            tick=tick,
        )

    def test_interleaved_lifecycles_and_id_reuse(self):
        events = (
            self.created("alpha", 0),
            self.created("beta", 0),
            self.collapsed("alpha", 1),
            self.disappeared("alpha", 2),
            self.created("alpha", 2),
            self.collapsed("beta", 3),
            self.disappeared("beta", 3),
        )

        remaining = QuantumBoxLifecycleValidator.validate(
            events
        )

        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].box_id, "alpha")
        self.assertEqual(remaining[0].created_tick, 2)
        self.assertIsNone(remaining[0].collapse_tick)

    def test_partial_history_is_valid(self):
        remaining = QuantumBoxLifecycleValidator.validate(
            (
                self.created(),
                self.collapsed(tick=1),
            )
        )

        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].collapse_tick, 1)
        self.assertEqual(
            remaining[0].collapse_cause,
            "opened",
        )

    def test_duplicate_active_creation_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (self.created(), self.created())
            )

    def test_collapse_without_creation_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (self.collapsed(),)
            )

    def test_duplicate_collapse_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (
                    self.created(),
                    self.collapsed(),
                    self.collapsed(),
                )
            )

    def test_disappearance_without_creation_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (self.disappeared(),)
            )

    def test_disappearance_before_collapse_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (
                    self.created(),
                    self.disappeared(),
                )
            )

    def test_collapse_and_disappearance_cause_must_match(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (
                    self.created(),
                    self.collapsed(cause="opened"),
                    self.disappeared(
                        cause="spontaneous",
                    ),
                )
            )

    def test_missing_collapse_cause_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (
                    self.created(),
                    self.collapsed(cause=""),
                )
            )

    def test_invalid_collapse_box_id_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (
                    self.created(),
                    self.collapsed(box_id=""),
                )
            )

    def test_negative_tick_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (self.created(tick=-1),)
            )

    def test_boolean_tick_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (
                    self.created(),
                    self.collapsed(tick=True),
                )
            )

    def test_decreasing_tick_is_rejected(self):
        with self.assertRaises(ValueError):
            QuantumBoxLifecycleValidator.validate(
                (
                    self.created(tick=2),
                    self.collapsed(tick=1),
                )
            )

    def test_unsupported_event_is_rejected(self):
        with self.assertRaises(TypeError):
            QuantumBoxLifecycleValidator.validate(
                (self.created(), object())
            )

    def test_invalid_late_event_is_atomic_for_universe(self):
        target = Universe(universe_id="validation")
        before = target.snapshot
        history = tuple(target.quantum_events)

        events = (
            self.created("alpha", 0),
            self.collapsed("alpha", 1),
            self.disappeared("alpha", 1),
            self.collapsed("alpha", 2),
        )

        with self.assertRaises(ValueError):
            target.replay_quantum_box_history(events)

        self.assertEqual(target.snapshot, before)
        self.assertEqual(
            tuple(target.quantum_events),
            history,
        )


if __name__ == "__main__":
    unittest.main()
