import unittest

from core.entity.cronenberg import Cronenberg
from core.entity.cronenberg_system.result_state import (
    CronenbergConsumptionResult,
)
from quantum.cronenberg_pair_encounter import (
    CronenbergQuantumPairNotEncounteredResult,
)
from universe.cronenberg_quantum_result_state import (
    CronenbergQuantumCounterpartCreatedEvent,
    CronenbergQuantumCounterpartCreatedResult,
    CronenbergQuantumPairConsumedEvent,
    CronenbergQuantumPairConsumptionResult,
    CronenbergQuantumPairMergedEvent,
    CronenbergQuantumPairMergeResult,
)
from universe.universe import Universe


class CronenbergQuantumResultObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(self, value):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(value, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = value["result"]

    def _create_pair(self):
        universe = Universe()
        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("result object test"),
                "test",
                "cronenberg_quantum_result_object_state",
            )
        )
        result = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )
        )
        return universe, original, result.counterpart

    def test_standard_consumption_returns_object(self):
        predator = Cronenberg(
            RuntimeError("predator"),
            "test",
            "consume",
        )
        prey = Cronenberg(
            RuntimeError("prey"),
            "test",
            "consume",
        )

        result = predator.consume(prey)

        self.assertIsInstance(
            result,
            CronenbergConsumptionResult,
        )
        self._assert_object_only(result)
        self.assertEqual(result.predator, predator.name)
        self.assertEqual(result.prey, prey.name)

    def test_counterpart_creation_returns_objects(self):
        universe = Universe()
        original = (
            universe
            .create_cronenberg_from_quantum_error(
                RuntimeError("counterpart"),
                "test",
                "counterpart",
            )
        )

        result = (
            universe
            .create_cronenberg_quantum_counterpart(
                original
            )
        )

        self.assertIsInstance(
            result,
            CronenbergQuantumCounterpartCreatedResult,
        )
        self.assertIsInstance(
            result.event,
            CronenbergQuantumCounterpartCreatedEvent,
        )
        self._assert_object_only(result)
        self._assert_object_only(result.event)
        self.assertIs(
            universe.quantum_events[-1],
            result.event,
        )

    def test_pair_merge_returns_objects(self):
        universe, first, second = self._create_pair()
        first.location = "shared_kernel"
        second.location = "shared_kernel"

        result = universe.merge_cronenberg_quantum_pair(
            first,
            second,
        )

        self.assertIsInstance(
            result,
            CronenbergQuantumPairMergeResult,
        )
        self.assertIsInstance(
            result.event,
            CronenbergQuantumPairMergedEvent,
        )
        self._assert_object_only(result)
        self._assert_object_only(result.event)
        self.assertIs(result.merged, universe.cronenbergs[-1])

    def test_pair_consumption_returns_objects(self):
        universe, first, second = self._create_pair()
        first.location = "shared_kernel"
        second.location = "shared_kernel"

        result = first.consume(second)

        self.assertIsInstance(
            result,
            CronenbergQuantumPairConsumptionResult,
        )
        self.assertIsInstance(
            result.event,
            CronenbergQuantumPairConsumedEvent,
        )
        self._assert_object_only(result)
        self._assert_object_only(result.event)
        self.assertIs(
            universe.quantum_events[-1],
            result.event,
        )

    def test_non_encounter_returns_object(self):
        universe, first, second = self._create_pair()
        first.location = "first_layer"
        second.location = "second_layer"

        result = (
            universe.cronenberg_pair_encounter
            .detect(first, second)
        )

        self.assertIsInstance(
            result,
            CronenbergQuantumPairNotEncounteredResult,
        )
        self._assert_object_only(result)
        self.assertFalse(result.encountered)
        self.assertEqual(
            result.reason,
            "different_location",
        )


if __name__ == "__main__":
    unittest.main()
