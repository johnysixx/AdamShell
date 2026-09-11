import unittest

from universe.energy_gate import EnergyGate
from universe.energy_gate_state import EnergyGateState
from universe.universe import Universe


class EnergyGateObjectStateTests(unittest.TestCase):

    def test_state_is_object_only(self):
        state = EnergyGateState(threshold_j=10.0)

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(state, mapping_method)
            )

        with self.assertRaises(TypeError):
            _ = state["big_bang_allowed"]

    def test_initial_values_are_preserved(self):
        state = EnergyGateState(threshold_j=10.0)

        self.assertEqual(state.threshold_j, 10.0)
        self.assertEqual(state.idea_energy_j, 0.0)
        self.assertEqual(state.energy_ratio, 0.0)
        self.assertFalse(state.threshold_reached)
        self.assertFalse(state.physical_seed_created)
        self.assertFalse(state.big_bang_allowed)
        self.assertFalse(state.big_bang_started)

    def test_collection_mutates_same_world_state(self):
        universe = Universe()
        gate = EnergyGate(universe, threshold_j=10.0)
        state = gate.gate_state

        result = gate.collect_energy("idea", 4.0)

        self.assertIs(gate.gate_state, state)
        self.assertIs(
            universe.world["energy_gate_state"],
            state,
        )
        self.assertEqual(state.idea_energy_j, 4.0)
        self.assertEqual(state.energy_ratio, 0.4)
        self.assertEqual(len(gate.events), 1)
        self.assertEqual(
            result["events"][0]["source"],
            "idea",
        )

    def test_public_result_is_deeply_detached_dict(self):
        universe = Universe()
        gate = EnergyGate(universe, threshold_j=10.0)
        result = gate.collect_energy("idea", 4.0)

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result["gate_state"], dict)
        self.assertIsInstance(result["events"], list)

        result["gate_state"]["idea_energy_j"] = 999.0
        result["events"][0]["source"] = "changed"

        self.assertEqual(gate.gate_state.idea_energy_j, 4.0)
        self.assertEqual(gate.events[0]["source"], "idea")

    def test_threshold_updates_closed_and_open_state(self):
        universe = Universe()
        gate = EnergyGate(universe, threshold_j=10.0)

        gate.collect_energy("first", 4.0)

        self.assertEqual(gate.state, "closed")
        self.assertFalse(gate.gate_state.threshold_reached)
        self.assertFalse(gate.gate_state.big_bang_allowed)

        gate.collect_energy("second", 6.0)

        self.assertEqual(gate.state, "open")
        self.assertTrue(gate.gate_state.threshold_reached)
        self.assertTrue(
            gate.gate_state.physical_seed_created
        )
        self.assertTrue(gate.gate_state.big_bang_allowed)

    def test_big_bang_respects_gate_and_starts_once_open(self):
        universe = Universe()
        gate = EnergyGate(universe, threshold_j=10.0)

        self.assertFalse(gate.try_start_big_bang())
        self.assertFalse(universe.big_bang_started)

        gate.collect_energy("idea", 10.0)

        self.assertTrue(gate.try_start_big_bang())
        self.assertTrue(universe.big_bang_started)
        self.assertTrue(gate.gate_state.big_bang_started)

    def test_invalid_amount_remains_validation_error(self):
        universe = Universe()
        gate = EnergyGate(universe, threshold_j=10.0)

        with self.assertRaises(ValueError):
            gate.collect_energy("idea", 0.0)

        self.assertEqual(universe.cronenbergs, [])

    def test_collection_error_creates_cronenberg(self):
        universe = Universe()
        gate = EnergyGate(universe, threshold_j=10.0)

        def broken_update():
            raise RuntimeError("energy collection exploded")

        gate._update_state_unprotected = broken_update

        result = gate.collect_energy("idea", 1.0)
        cronenberg = result["cronenberg"]

        self.assertIn(cronenberg, universe.cronenbergs)
        self.assertEqual(
            cronenberg.origin.source_component,
            "energy_gate",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "collect_energy",
        )

    def test_update_error_creates_cronenberg(self):
        universe = Universe()
        gate = EnergyGate(universe, threshold_j=10.0)
        gate.threshold_j = "broken"

        result = gate.update_state()
        cronenberg = result["cronenberg"]

        self.assertIn(cronenberg, universe.cronenbergs)
        self.assertEqual(
            cronenberg.origin.source_operation,
            "update_state",
        )

    def test_start_error_creates_cronenberg(self):
        universe = Universe()
        gate = EnergyGate(universe, threshold_j=10.0)
        gate.collect_energy("idea", 10.0)

        def broken_start():
            raise RuntimeError("big bang start exploded")

        universe.start_big_bang = broken_start

        result = gate.try_start_big_bang()
        cronenberg = result["cronenberg"]

        self.assertIn(cronenberg, universe.cronenbergs)
        self.assertEqual(
            cronenberg.origin.source_operation,
            "try_start_big_bang",
        )

    def test_to_dict_is_detached_boundary(self):
        state = EnergyGateState(threshold_j=10.0)
        state.big_bang_allowed = True

        snapshot = state.to_dict()
        snapshot["big_bang_allowed"] = False

        self.assertTrue(state.big_bang_allowed)


if __name__ == "__main__":
    unittest.main()
