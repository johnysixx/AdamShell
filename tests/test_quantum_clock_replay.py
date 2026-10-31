import unittest
from dataclasses import FrozenInstanceError
from unittest.mock import patch

from universe.quantum_tick_advanced_state import (
    UniverseQuantumTickAdvancedEvent,
)
from universe.universe import Universe


class QuantumClockReplayTests(unittest.TestCase):

    def make_history(self, count=3):
        source = Universe(universe_id="clock")
        source.enable_quantum_layer()

        for _ in range(count):
            source.tick_quantum_unprotected()

        return source, tuple(source.quantum_clock_events)

    def make_target(self):
        target = Universe(universe_id="clock")
        target.enable_quantum_layer()
        return target

    def test_disabled_clock_records_no_events(self):
        universe = Universe(universe_id="disabled")

        result = universe.tick_quantum_unprotected()

        self.assertIsNone(result)
        self.assertEqual(universe.quantum_clock_events, [])
        self.assertEqual(universe.quantum_events, [])
        self.assertEqual(universe.quantum_state.tick_count, 0)

    def test_ticks_record_immutable_ordered_events(self):
        source, events = self.make_history()

        self.assertEqual([e.tick for e in events], [1, 2, 3])
        self.assertTrue(
            all(
                isinstance(
                    event,
                    UniverseQuantumTickAdvancedEvent,
                )
                for event in events
            )
        )
        self.assertEqual(
            [event.observer for event in events],
            ["quantum_tick"] * 3,
        )
        self.assertEqual(source.quantum_events, [])

    def test_clock_replay_restores_complete_state(self):
        source, events = self.make_history()
        target = self.make_target()
        original_state = target.quantum_state

        result = target.replay_quantum_clock_history(events)

        self.assertIs(result, original_state)
        self.assertIs(target.quantum_state, original_state)
        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )
        self.assertEqual(target.quantum_clock_events, [])
        self.assertEqual(target.quantum_events, [])

    def test_clock_replay_accepts_generator(self):
        source, events = self.make_history(4)
        target = self.make_target()

        target.replay_quantum_clock_history(
            event for event in events
        )

        self.assertEqual(
            target.quantum_state.to_dict(),
            source.quantum_state.to_dict(),
        )

    def test_missing_tick_is_rejected_atomically(self):
        _, events = self.make_history()
        target = self.make_target()
        before = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            target.replay_quantum_clock_history(
                (events[0], events[2])
            )

        self.assertEqual(
            target.quantum_state.to_dict(),
            before,
        )

    def test_duplicate_tick_is_rejected_atomically(self):
        _, events = self.make_history()
        target = self.make_target()
        before = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            target.replay_quantum_clock_history(
                (events[0], events[1], events[1])
            )

        self.assertEqual(
            target.quantum_state.to_dict(),
            before,
        )

    def test_unsupported_event_is_rejected_atomically(self):
        _, events = self.make_history()
        target = self.make_target()
        before = target.quantum_state.to_dict()

        with self.assertRaises(TypeError):
            target.replay_quantum_clock_history(
                (events[0], {"tick": 2})
            )

        self.assertEqual(
            target.quantum_state.to_dict(),
            before,
        )

    def test_clock_must_be_enabled_for_nonempty_replay(self):
        _, events = self.make_history()
        target = Universe(universe_id="disabled-target")
        before = target.quantum_state.to_dict()

        with self.assertRaises(ValueError):
            target.replay_quantum_clock_history(events)

        self.assertEqual(
            target.quantum_state.to_dict(),
            before,
        )

    def test_existing_clock_state_is_preserved(self):
        _, events = self.make_history()
        target = self.make_target()
        target.tick_quantum_unprotected()
        before = target.quantum_state.to_dict()
        history = tuple(target.quantum_clock_events)

        with self.assertRaises(ValueError):
            target.replay_quantum_clock_history(events)

        self.assertEqual(
            target.quantum_state.to_dict(),
            before,
        )
        self.assertEqual(
            tuple(target.quantum_clock_events),
            history,
        )

    def test_replay_does_not_run_box_simulation(self):
        _, events = self.make_history()
        target = self.make_target()

        with patch.object(
            target,
            "should_collapse_quantum_box",
            side_effect=AssertionError(
                "Box simulation was invoked."
            ),
        ):
            target.replay_quantum_clock_history(events)

        self.assertEqual(target.quantum_state.tick_count, 3)
        self.assertEqual(target.statistics.total_quantum_collapses, 0)

    def test_replay_does_not_use_rng_or_uuid(self):
        _, events = self.make_history()
        target = self.make_target()

        with (
            patch(
                "core.entity.quantum_box.random.choice",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.random.uniform",
                side_effect=AssertionError("RNG used"),
            ),
            patch(
                "core.entity.quantum_box.uuid.uuid4",
                side_effect=AssertionError("UUID used"),
            ),
        ):
            target.replay_quantum_clock_history(events)

        self.assertEqual(target.quantum_state.tick_count, 3)

    def test_event_contract_is_strict_and_immutable(self):
        for invalid in (0, -1, True, 1.5, "1", None):
            with self.subTest(tick=invalid):
                with self.assertRaises(ValueError):
                    UniverseQuantumTickAdvancedEvent(
                        tick=invalid,
                    )

        with self.assertRaises(ValueError):
            UniverseQuantumTickAdvancedEvent(
                tick=1,
                observer="",
            )

        event = UniverseQuantumTickAdvancedEvent(tick=1)

        with self.assertRaises(FrozenInstanceError):
            event.tick = 99

        exported = event.to_dict()
        exported["tick"] = 99
        self.assertEqual(event.tick, 1)

    def test_empty_history_is_noop(self):
        target = Universe(universe_id="empty")
        before = target.quantum_state.to_dict()

        target.replay_quantum_clock_history(())

        self.assertEqual(
            target.quantum_state.to_dict(),
            before,
        )


if __name__ == "__main__":
    unittest.main()
