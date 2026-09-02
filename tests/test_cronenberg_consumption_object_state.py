import unittest
from dataclasses import FrozenInstanceError

from core.entity.cronenberg import Cronenberg
from core.entity.cronenberg_system.consumption import (
    CronenbergConsumptionRecord
)


class CronenbergConsumptionObjectStateTests(
    unittest.TestCase
):

    def _create_cronenberg(self, label):
        return Cronenberg(
            error=RuntimeError(label),
            source_component="consumption_test",
            source_operation=label,
        )

    def _assert_object_only(self, value):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method
                )
            )

        with self.assertRaises(TypeError):
            _ = value["name"]

    def test_consumption_stores_object_record(
        self
    ):
        predator = self._create_cronenberg(
            "predator"
        )
        prey = self._create_cronenberg("prey")
        prey.size = 1.5
        prey.energy = 0.75

        event = predator.consume(prey)

        self.assertEqual(
            len(predator.consumed_cronenbergs),
            1
        )
        record = predator.consumed_cronenbergs[0]
        self.assertIsInstance(
            record,
            CronenbergConsumptionRecord
        )
        self._assert_object_only(record)
        self.assertEqual(record.name, prey.name)
        self.assertEqual(record.mass, 1.5)
        self.assertEqual(record.energy, 0.75)
        self.assertEqual(
            record.digestion_days,
            event["digestion_days"]
        )

    def test_record_is_immutable_after_capture(
        self
    ):
        predator = self._create_cronenberg(
            "predator"
        )
        prey = self._create_cronenberg("prey")
        predator.consume(prey)
        record = predator.consumed_cronenbergs[0]

        with self.assertRaises(
            FrozenInstanceError
        ):
            record.mass = 99.0

    def test_consumption_preserves_prey_transition(
        self
    ):
        predator = self._create_cronenberg(
            "predator"
        )
        prey = self._create_cronenberg("prey")

        predator.consume(prey)

        self.assertEqual(
            prey.state,
            "consumed_by_cronenberg"
        )
        self.assertEqual(
            prey.location,
            "inside_cronenberg"
        )
        self.assertEqual(prey.energy, 0.0)

    def test_public_history_is_detached_dicts(
        self
    ):
        predator = self._create_cronenberg(
            "predator"
        )
        prey = self._create_cronenberg("prey")
        prey.size = 1.25
        predator.consume(prey)

        snapshot = predator.public_state[
            "consumed_cronenbergs"
        ]

        self.assertIsInstance(snapshot, list)
        self.assertIsInstance(snapshot[0], dict)
        snapshot[0]["name"] = "changed"
        snapshot[0]["mass"] = 99.0

        record = predator.consumed_cronenbergs[0]
        self.assertEqual(record.name, prey.name)
        self.assertEqual(record.mass, 1.25)


if __name__ == "__main__":
    unittest.main()
