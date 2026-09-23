import unittest

from universe.dark_sector import DarkSector
from universe.dark_sector_state import (
    DarkMatterCondensationEvent,
    DarkSectorEnergyReceivedEvent,
    DarkSectorState,
)
from universe.universe import Universe


class DarkSectorObjectStateTests(unittest.TestCase):

    def test_state_is_object_only(self):
        state = DarkSectorState(quantum_threshold_j=10.0)

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
            _ = state["dark_energy_j"]

    def test_initial_values_are_preserved(self):
        state = DarkSectorState(quantum_threshold_j=10.0)

        self.assertEqual(state.quantum_threshold_j, 10.0)
        self.assertEqual(state.dark_energy_j, 0.0)
        self.assertEqual(state.dark_matter_kg, 0.0)

    def test_universe_dark_sector_owns_state_object(self):
        universe = Universe()
        sector = universe.dark_sector

        self.assertIsInstance(
            sector.dark_sector_state,
            DarkSectorState,
        )
        self.assertIs(sector.universe, universe)

    def test_scalar_interface_mutates_object_state(self):
        sector = DarkSector()
        state = sector.dark_sector_state

        sector.dark_energy_j = 4.0
        sector.dark_matter_kg = 2.0
        sector.quantum_threshold_j = 8.0

        self.assertIs(sector.dark_sector_state, state)
        self.assertEqual(state.dark_energy_j, 4.0)
        self.assertEqual(state.dark_matter_kg, 2.0)
        self.assertEqual(state.quantum_threshold_j, 8.0)

    def test_receiving_energy_mutates_same_state(self):
        universe = Universe()
        sector = universe.dark_sector
        state = sector.dark_sector_state

        event = sector.receive_empty_box_energy(
            box_id="empty_box",
            energy_j=2.0,
        )

        self.assertIs(sector.dark_sector_state, state)
        self.assertEqual(state.dark_energy_j, 2.0)
        self.assertIsInstance(
            event,
            DarkSectorEnergyReceivedEvent,
        )
        self.assertIs(
            sector.events[0],
            event,
        )
        self.assertEqual(
            event.box_id,
            "empty_box",
        )
        self.assertEqual(
            event.energy_j,
            2.0,
        )

    def test_public_state_is_detached_dict_boundary(self):
        sector = DarkSector()
        sector.receive_empty_box_energy(
            box_id="empty_box",
            energy_j=2.0,
        )

        public_state = sector.public_state

        self.assertIsInstance(public_state, dict)
        self.assertIsInstance(
            public_state["dark_sector_state"],
            dict,
        )

        public_state["dark_sector_state"][
            "dark_energy_j"
        ] = 999.0

        self.assertEqual(sector.dark_energy_j, 2.0)

    def test_condensation_mutates_same_state_object(self):
        sector = DarkSector()
        state = sector.dark_sector_state
        sector.quantum_threshold_j = 10.0
        sector.dark_energy_j = 10.0

        event = sector._condense_dark_matter()

        self.assertIs(sector.dark_sector_state, state)
        self.assertEqual(state.dark_energy_j, 0.0)
        self.assertGreater(state.dark_matter_kg, 0.0)
        self.assertIsInstance(
            event,
            DarkMatterCondensationEvent,
        )
        self.assertEqual(
            event.dark_energy_remaining_j,
            0.0,
        )

    def test_dark_sector_events_are_object_only(self):
        sector = DarkSector()

        event = sector.receive_empty_box_energy(
            box_id="empty_box",
            energy_j=2.0,
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
            _ = event["energy_j"]

        snapshot = event.to_dict()
        snapshot["energy_j"] = 999.0

        self.assertEqual(
            event.energy_j,
            2.0,
        )

    def test_invalid_energy_remains_validation_error(self):
        universe = Universe()
        sector = universe.dark_sector

        with self.assertRaises(ValueError):
            sector.receive_empty_box_energy(
                box_id="empty_box",
                energy_j=0.0,
            )

        self.assertEqual(universe.cronenbergs, [])

    def test_receiving_error_creates_cronenberg(self):
        universe = Universe()
        sector = universe.dark_sector
        sector.events = None

        result = sector.receive_empty_box_energy(
            box_id="broken_box",
            energy_j=1.0,
        )
        cronenberg = result["cronenberg"]

        self.assertEqual(result["type"], "quantum_error")
        self.assertIn(cronenberg, universe.cronenbergs)
        self.assertEqual(
            cronenberg.origin.source_component,
            "dark_sector",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "receive_empty_box_energy",
        )

    def test_standalone_dark_sector_stays_supported(self):
        sector = DarkSector()

        result = sector.receive_empty_box_energy(
            box_id="empty_box",
            energy_j=1.0,
        )

        self.assertIsInstance(
            result,
            DarkSectorEnergyReceivedEvent,
        )
        self.assertEqual(
            result.energy_j,
            1.0,
        )
        self.assertEqual(
            sector.dark_energy_j,
            1.0,
        )

    def test_to_dict_is_detached_boundary(self):
        state = DarkSectorState(quantum_threshold_j=10.0)
        state.dark_energy_j = 5.0

        snapshot = state.to_dict()
        snapshot["dark_energy_j"] = 999.0

        self.assertEqual(state.dark_energy_j, 5.0)


if __name__ == "__main__":
    unittest.main()
