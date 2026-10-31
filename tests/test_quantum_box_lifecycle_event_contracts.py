import unittest

from core.entity.components import SpatialVector3
from core.entity.quantum_box import QuantumBox
from core.entity.quantum_box_operation_result_state import (
    QuantumBoxCollapsedEvent,
)
from universe.quantum_box_creation_state import (
    QuantumBoxCreatedEvent,
)
from universe.quantum_box_disappearance_state import (
    QuantumBoxDisappearedEvent,
)
from universe.universe import Universe


class QuantumBoxLifecycleEventContractsTests(
    unittest.TestCase
):

    def created(self, tick=0, box_id="boundary_box"):
        return QuantumBoxCreatedEvent(
            box_id=box_id,
            position=SpatialVector3(
                x=0.0,
                y=0.0,
                z=0.0,
            ),
            layer="quantum_layer",
            tick=tick,
        )

    def collapsed(
        self,
        tick=0,
        box_id="boundary_box",
        result="empty",
        cause="opened",
        observer=None,
    ):
        return QuantumBoxCollapsedEvent(
            quantum_box_id=box_id,
            result=result,
            cause=cause,
            observer=observer,
            tick=tick,
        )

    def disappeared(
        self,
        tick=0,
        box_id="boundary_box",
        cause="opened",
    ):
        return QuantumBoxDisappearedEvent(
            box_id=box_id,
            cause=cause,
            tick=tick,
        )

    def test_valid_events_preserve_fields(self):
        created = self.created(tick=2)
        collapsed = self.collapsed(
            tick=3,
            observer="tester",
        )
        disappeared = self.disappeared(tick=4)

        self.assertEqual(created.tick, 2)
        self.assertEqual(collapsed.tick, 3)
        self.assertEqual(collapsed.observer, "tester")
        self.assertEqual(disappeared.tick, 4)
        self.assertEqual(
            created.name,
            "quantum_box_created",
        )
        self.assertEqual(
            collapsed.name,
            "quantum_box_collapsed",
        )
        self.assertEqual(
            disappeared.name,
            "quantum_box_disappeared",
        )

    def test_created_tick_is_strict_integer(self):
        for invalid in (
            None,
            True,
            False,
            -1,
            "1",
            1.0,
        ):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    self.created(tick=invalid)

    def test_disappeared_tick_is_strict_integer(self):
        for invalid in (
            None,
            True,
            False,
            -1,
            "1",
            1.0,
        ):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    self.disappeared(tick=invalid)

    def test_collapse_accepts_optional_tick(self):
        without_tick = self.collapsed(tick=None)
        with_tick = self.collapsed(tick=0)

        self.assertIsNone(without_tick.tick)
        self.assertEqual(with_tick.tick, 0)

    def test_collapsed_tick_rejects_invalid_values(self):
        for invalid in (
            True,
            False,
            -1,
            "1",
            1.0,
        ):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    self.collapsed(tick=invalid)

    def test_collapsed_id_rejects_invalid_values(self):
        for invalid in (
            None,
            "",
            123,
        ):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    self.collapsed(box_id=invalid)

    def test_collapsed_result_rejects_invalid_values(self):
        for invalid in (
            None,
            "",
            123,
            False,
        ):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    self.collapsed(result=invalid)

    def test_collapsed_cause_rejects_invalid_values(self):
        for invalid in (
            None,
            "",
            123,
        ):
            with self.subTest(value=invalid):
                with self.assertRaises(ValueError):
                    self.collapsed(cause=invalid)

    def test_collapsed_observer_rejects_invalid_values(self):
        for invalid in (
            123,
            False,
            object(),
        ):
            with self.subTest(value=type(invalid).__name__):
                with self.assertRaises(ValueError):
                    self.collapsed(observer=invalid)

    def test_invalid_collapse_metadata_leaves_box_unchanged(self):
        box = QuantumBox(
            box_id="boundary_box",
            position=SpatialVector3(
                x=0.0, y=0.0, z=0.0,
            ),
        )

        before = box.public_state

        bad_metadata = (
            {"cause": ""},
            {"cause": "opened", "observer": 123},
            {"cause": "opened", "tick": -1},
            {"cause": "opened", "tick": True},
        )

        for metadata in bad_metadata:
            with self.subTest(metadata=metadata):
                with self.assertRaises(ValueError):
                    box.resolve_state(
                        result="empty",
                        **metadata,
                    )

                self.assertEqual(
                    box.public_state,
                    before,
                )
                self.assertFalse(
                    box.collapse.collapsed
                )

    def test_unknown_result_remains_operation_validation(self):
        event = self.collapsed(
            result="not_a_valid_possibility",
        )

        target = Universe(universe_id="boundary")
        target.create_quantum_box(
            box_id="boundary_box",
        )

        before = target.snapshot

        with self.assertRaises(ValueError):
            target.replay_quantum_box_collapsed(event)

        self.assertEqual(target.snapshot, before)
        self.assertEqual(
            target.statistics.total_quantum_collapses,
            0,
        )


if __name__ == "__main__":
    unittest.main()
