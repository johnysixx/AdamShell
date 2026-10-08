import unittest

from cats.physical_biology_gate import (
    PhysicalBiologyGate,
    PhysicalBiologyGateBlockedEvent,
    PhysicalBiologyGateResult,
)


class FakeCronenberg:

    def __init__(
        self,
        cronenberg_id,
    ):
        self.id = cronenberg_id


class FakeUniverse:

    def __init__(
        self,
        started=False,
    ):
        self.physical_universe_started = started
        self.quantum_events = []

    def create_cronenberg_from_quantum_error(
        self,
        error,
        source_component,
        source_operation,
    ):
        return FakeCronenberg(
            "cronenberg_gate_test"
        )


class FakeCat:
    name = "gate_cat"


class PhysicalBiologyGateObjectStateTests(
    unittest.TestCase
):

    def test_blocked_history_uses_object_state(
        self
    ):
        universe = FakeUniverse(
            started=False
        )

        gate = PhysicalBiologyGate(
            universe
        )

        result = (
            gate.require_physical_world(
                operation="reproduce",
                cat=FakeCat(),
            )
        )

        event = gate.history[-1]

        self.assertIsInstance(
            result,
            PhysicalBiologyGateResult,
        )

        self.assertIsInstance(
            event,
            PhysicalBiologyGateBlockedEvent,
        )

        self.assertIs(
            result.event,
            event,
        )

        self.assertFalse(
            result.allowed
        )

        self.assertEqual(
            event.operation,
            "reproduce",
        )

        self.assertEqual(
            event.cat,
            "gate_cat",
        )

        self.assertFalse(
            event.allowed
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    event,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = event["operation"]

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = result[
                "operation"
            ]

        self.assertEqual(
            result.operation,
            "reproduce",
        )

        self.assertEqual(
            result.cronenberg.id,
            "cronenberg_gate_test",
        )

        universe.quantum_events[
            0
        ][
            "operation"
        ] = "changed_again"

        self.assertEqual(
            event.operation,
            "reproduce",
        )

    def test_allowed_path_does_not_record_history(
        self
    ):
        universe = FakeUniverse(
            started=True
        )

        gate = PhysicalBiologyGate(
            universe
        )

        result = (
            gate.require_physical_world(
                operation="reproduce",
                cat=FakeCat(),
            )
        )

        self.assertIsInstance(
            result,
            PhysicalBiologyGateResult,
        )

        self.assertTrue(
            result.allowed
        )

        self.assertIsNone(
            result.event
        )

        self.assertIsNone(
            result.cronenberg
        )

        with self.assertRaises(TypeError):
            _ = result[
                "allowed"
            ]

        self.assertEqual(
            gate.history,
            [],
        )

    def test_history_rejects_mapping_event(
        self
    ):
        gate = PhysicalBiologyGate(
            FakeUniverse()
        )

        with self.assertRaises(TypeError):
            gate.record_event(
                {
                    "name": (
                        "premature_cat_biology_"
                        "replaced_by_cronenberg"
                    ),
                }
            )


if __name__ == "__main__":
    unittest.main()
