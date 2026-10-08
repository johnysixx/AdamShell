import unittest
from types import SimpleNamespace

from core.entity.cat_quantum_transfer_phase import (
    CatQuantumTransferPhase,
)
from core.entity.quantum_box import QuantumBox
from core.entity.quantum_box_operation_result_state import (
    QuantumBoxAlreadyCollapsedResult,
    QuantumBoxCatTransferEnergyConsumedEvent,
    QuantumBoxCatTransferStartedEvent,
    QuantumBoxCollapsedEvent,
    QuantumBoxCounterpartClearedEvent,
)


class QuantumBoxOperationResultsObjectStateTests(
    unittest.TestCase
):

    def assert_object_only(
        self,
        value,
    ):
        for name in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    name,
                ),
                name,
            )

        with self.assertRaises(
            TypeError
        ):
            _ = value["name"]

    def test_counterpart_clear_returns_object(
        self
    ):
        source = QuantumBox()
        target = QuantumBox()

        source.pair_with(
            target
        )

        result = (
            source.clear_counterpart()
        )

        self.assertIsInstance(
            result,
            QuantumBoxCounterpartClearedEvent,
        )

        self.assertTrue(
            result.was_paired
        )

        self.assertEqual(
            result.previous_box_id,
            target.id,
        )

        self.assert_object_only(
            result
        )

    def test_transfer_start_returns_object(
        self
    ):
        source = QuantumBox()
        target = QuantumBox()

        source.pair_with(
            target
        )

        cat = SimpleNamespace(
            name="traveller",
            type="cat",
        )

        result = (
            source.begin_cat_transfer(
                cat=cat,
                target_box=target,
                tick=7,
            )
        )

        self.assertIsInstance(
            result,
            QuantumBoxCatTransferStartedEvent,
        )

        self.assertTrue(
            result.active
        )

        self.assertIs(
            result.state,
            CatQuantumTransferPhase.SUPERPOSITION,
        )

        self.assertEqual(
            result.started_tick,
            7,
        )

        self.assert_object_only(
            result
        )

    def test_energy_consumption_returns_object(
        self
    ):
        box = QuantumBox()

        result = (
            box.consume_for_cat_transfer()
        )

        self.assertIsInstance(
            result,
            QuantumBoxCatTransferEnergyConsumedEvent,
        )

        self.assertTrue(
            result.consumed
        )

        self.assertFalse(
            result.available
        )

        self.assert_object_only(
            result
        )

    def test_collapse_returns_object(
        self
    ):
        box = QuantumBox()

        result = box.resolve_state(
            result="cat",
            cause="observation",
            observer="pazuzu",
            tick=9,
        )

        self.assertIsInstance(
            result,
            QuantumBoxCollapsedEvent,
        )

        self.assertEqual(
            result.result,
            "cat",
        )

        self.assertTrue(
            result.changed
        )

        self.assert_object_only(
            result
        )

    def test_repeated_collapse_returns_object(
        self
    ):
        box = QuantumBox()

        box.resolve_state(
            result="cat",
            cause="observation",
        )

        result = box.resolve_state(
            result="empty",
            cause="second_observation",
        )

        self.assertIsInstance(
            result,
            QuantumBoxAlreadyCollapsedResult,
        )

        self.assertEqual(
            result.result,
            "cat",
        )

        self.assertFalse(
            result.changed
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
