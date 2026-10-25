import unittest
from copy import deepcopy
from dataclasses import FrozenInstanceError

from universe.universe import Universe
from universe.universe_history_state import (
    UniverseHistorySnapshot,
)


class UniverseHistoryObjectStateTests(unittest.TestCase):

    def test_classical_history_uses_domain_objects(self):
        universe = Universe()

        universe.last_energy_gain = 2.5
        universe.last_pressure_cost = 1.25
        universe.last_energy_delta = 1.25

        universe.record_universe_state()

        record = universe.universe_history[-1]

        self.assertIsInstance(
            record,
            UniverseHistorySnapshot,
        )

        self.assertEqual(record.tick, 0)
        self.assertEqual(record.energy, 100)
        self.assertEqual(record.gain, 2.5)
        self.assertEqual(record.cost, 1.25)
        self.assertEqual(record.delta, 1.25)
        self.assertEqual(
            record.physics_model,
            "symbolic_classical",
        )
        self.assertFalse(record.quantum_enabled)

    def test_history_objects_are_immutable(self):
        universe = Universe()
        universe.record_universe_state()

        record = universe.universe_history[-1]

        with self.assertRaises(FrozenInstanceError):
            record.energy = 999.0

        with self.assertRaises(TypeError):
            _ = record["energy"]

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(record, mapping_method)
            )

        self.assertIs(
            deepcopy(record),
            record,
        )

    def test_snapshot_export_is_detached(self):
        universe = Universe()
        universe.record_universe_state()

        record = universe.universe_history[-1]

        first = record.to_dict()

        first["tick"] = 999
        first["energy"] = -1000
        first["physics_model"] = "changed"

        second = record.to_dict()

        self.assertEqual(second["tick"], 0)
        self.assertEqual(second["energy"], 100)
        self.assertEqual(
            second["physics_model"],
            "symbolic_classical",
        )

        self.assertEqual(
            set(second),
            {
                "tick",
                "energy",
                "gain",
                "cost",
                "delta",
                "classical_entropy_delta",
                "classical_entropy_total",
                "entropy",
                "pressure",
                "curvature",
                "physics_model",
                "quantum_enabled",
                "quantum_fluctuation",
                "quantum_uncertainty",
                "quantum_entropy_delta",
                "quantum_entropy_total",
            },
        )

    def test_quantum_history_captures_values(self):
        universe = Universe()
        universe.enable_quantum_layer()
        universe.tick_quantum_unprotected()

        universe.record_universe_state()

        record = universe.universe_history[-1]

        self.assertIsInstance(
            record,
            UniverseHistorySnapshot,
        )
        self.assertEqual(
            record.physics_model,
            "symbolic_quantum",
        )
        self.assertTrue(record.quantum_enabled)
        self.assertEqual(
            record.quantum_fluctuation,
            universe.quantum_state.fluctuation,
        )
        self.assertEqual(
            record.quantum_uncertainty,
            universe.quantum_state.uncertainty,
        )
        self.assertEqual(
            record.quantum_entropy_delta,
            universe.quantum_state.entropy_delta,
        )
        self.assertEqual(
            record.quantum_entropy_total,
            universe.quantum_state.entropy_total,
        )

    def test_multiple_snapshots_keep_original_values(self):
        universe = Universe()

        universe.record_universe_state()
        first = universe.universe_history[-1]

        universe.universe_tick = 1
        universe.energy_pool += 10
        universe.entropy = 0.5

        universe.record_universe_state()
        second = universe.universe_history[-1]

        self.assertIsNot(first, second)
        self.assertEqual(
            len(universe.universe_history),
            2,
        )

        self.assertEqual(first.tick, 0)
        self.assertEqual(first.energy, 100)
        self.assertEqual(first.entropy, 0)

        self.assertEqual(second.tick, 1)
        self.assertEqual(second.energy, 110)
        self.assertEqual(second.entropy, 0.5)

    def test_tick_history_keeps_object_records(self):
        universe = Universe()

        report = universe.tick_universe()

        self.assertEqual(report.tick, 1)
        self.assertEqual(
            len(universe.universe_history),
            1,
        )

        record = universe.universe_history[-1]

        self.assertIsInstance(
            record,
            UniverseHistorySnapshot,
        )
        self.assertEqual(record.tick, report.tick)

        history_phase = next(
            phase
            for phase in report.phases
            if phase.phase == "history"
        )

        self.assertTrue(history_phase.ok)


if __name__ == "__main__":
    unittest.main()
