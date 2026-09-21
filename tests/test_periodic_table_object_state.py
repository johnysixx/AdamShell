import unittest

from universe.chemical_objects import ChemicalElement
from universe.periodic_table import PeriodicTable
from universe.periodic_table_state import (
    PeriodicTableRegistryState,
)
from universe.universe import Universe


class PeriodicTableObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(
        self,
        value,
        key,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def _built_table(self):
        universe = Universe()
        table = PeriodicTable(universe)
        result = table.build_known_table()

        return universe, table, result

    def test_registry_state_is_object_only(self):
        state = PeriodicTableRegistryState()

        self._assert_object_only(
            state,
            "known_element_count",
        )

    def test_initial_values_are_preserved(self):
        state = PeriodicTableRegistryState()

        self.assertFalse(
            state.known_elements_registered
        )
        self.assertEqual(state.known_element_count, 0)
        self.assertTrue(
            state.future_element_generation_available
        )
        self.assertEqual(state.future_element_count, 0)

    def test_build_mutates_same_state_object(self):
        universe = Universe()
        table = PeriodicTable(universe)
        state = table.registry_state

        table.build_known_table()

        self.assertIs(table.registry_state, state)
        self.assertTrue(
            state.known_elements_registered
        )
        self.assertEqual(state.known_element_count, 118)
        self.assertTrue(
            state.future_element_generation_available
        )
        self.assertEqual(state.future_element_count, 0)

    def test_world_registry_stores_state_object(
        self
    ):
        universe, table, _ = self._built_table()

        state = universe.world[
            "element_registry_state"
        ]
        self.assertIsInstance(
            state,
            PeriodicTableRegistryState,
        )
        self.assertIs(state, table.registry_state)
        self.assertIsInstance(
            universe.world[
                "elements_by_atomic_number"
            ],
            dict,
        )
        self.assertIsInstance(
            universe.world["future_elements"],
            dict,
        )
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._built_table()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["registry_state"],
            dict,
        )
        self.assertEqual(
            result["registry_state"][
                "known_element_count"
            ],
            118,
        )

    def test_public_result_is_detached(self):
        _, table, result = self._built_table()

        result["registry_state"][
            "known_element_count"
        ] = 999

        self.assertEqual(
            table.registry_state.known_element_count,
            118,
        )

    def test_future_element_updates_same_state_object(
        self
    ):
        universe, table, _ = self._built_table()
        state = table.registry_state

        element = table.create_future_element(119)

        self.assertIs(table.registry_state, state)
        self.assertEqual(state.future_element_count, 1)
        self.assertIsInstance(
            element,
            ChemicalElement,
        )
        self._assert_object_only(
            element,
            "atomic_number",
        )
        self.assertIs(
            universe.world[
                "element_registry_state"
            ],
            state,
        )
        self.assertEqual(
            universe.world["periodic_table"][
                "registry_state"
            ]["future_element_count"],
            1,
        )

    def test_build_error_creates_cronenberg(self):
        universe = Universe()
        table = PeriodicTable(universe)

        def broken_element(*args, **kwargs):
            raise RuntimeError(
                "periodic table exploded"
            )

        table.create_known_element = broken_element

        result = table.build_known_table()
        cronenberg = result["cronenberg"]

        self.assertEqual(
            result["type"],
            "quantum_error",
        )
        self.assertIn(
            cronenberg,
            universe.cronenbergs,
        )
        self.assertEqual(
            cronenberg.origin.source_component,
            "periodic_table",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "build_known_table",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "periodic table exploded",
        )

    def test_to_dict_is_detached_boundary(self):
        state = PeriodicTableRegistryState()
        state.known_element_count = 118

        snapshot = state.to_dict()
        snapshot["known_element_count"] = 999

        self.assertEqual(state.known_element_count, 118)


if __name__ == "__main__":
    unittest.main()
