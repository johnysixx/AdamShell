import unittest

from idea_universe.primordial_nebula import PrimordialNebula
from idea_universe.primordial_nebula_state import (
    PrimordialNebulaState,
)


class PrimordialNebulaObjectStateTests(unittest.TestCase):

    def _nebula_with_elements(self):
        return PrimordialNebula(
            source_remnants=[
                {
                    "name": "remnant",
                    "elemental_potentials": {
                        "hydrogen": 2.0,
                        "carbon": 1.0,
                    },
                },
            ],
        )

    def test_state_is_object_only(self):
        state = PrimordialNebulaState()

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
            _ = state["size"]

    def test_initial_values_are_preserved(self):
        nebula = PrimordialNebula()
        state = nebula.primordial_nebula_state

        self.assertIs(nebula.state, state)
        self.assertEqual(state.tick_count, 0)
        self.assertEqual(state.size, 0.0)
        self.assertEqual(state.stars, [])
        self.assertEqual(state.source_remnants, [])
        self.assertEqual(state.source_remnant_count, 0)
        self.assertEqual(state.elemental_potentials, {})
        self.assertIsNone(
            state.previous_liquid_hydrocarbon_level
        )
        self.assertEqual(
            state.current_liquid_hydrocarbon_level,
            0.0,
        )
        self.assertEqual(state.mined_from_current_growth, 0.0)

    def test_remnants_are_aggregated_into_object_state(self):
        nebula = self._nebula_with_elements()
        state = nebula.primordial_nebula_state

        self.assertEqual(state.source_remnant_count, 1)
        self.assertIs(nebula.source_remnants, state.source_remnants)
        self.assertIs(
            nebula.elemental_potentials,
            state.elemental_potentials,
        )
        self.assertEqual(
            state.elemental_potentials,
            {
                "hydrogen": 2.0,
                "carbon": 1.0,
            },
        )

    def test_scalar_interface_mutates_same_state_object(self):
        nebula = PrimordialNebula()
        state = nebula.primordial_nebula_state

        nebula.size = 100.0
        nebula.tick_count = 4
        nebula.current_liquid_hydrocarbon_level = 20.0

        self.assertIs(nebula.primordial_nebula_state, state)
        self.assertEqual(state.size, 100.0)
        self.assertEqual(state.tick_count, 4)
        self.assertEqual(
            state.current_liquid_hydrocarbon_level,
            20.0,
        )

    def test_hydrocarbon_formation_mutates_same_state(self):
        nebula = self._nebula_with_elements()
        state = nebula.primordial_nebula_state
        potentials = state.elemental_potentials

        amount = nebula.form_hydrocarbons()
        nebula.size = 10.0
        liquid_amount = nebula.form_liquid_hydrocarbons()

        self.assertIs(nebula.primordial_nebula_state, state)
        self.assertIs(state.elemental_potentials, potentials)
        self.assertEqual(amount, 1.0)
        self.assertEqual(liquid_amount, 1.0)
        self.assertEqual(potentials["hydrocarbons"], 1.0)
        self.assertEqual(potentials["liquid_hydrocarbons"], 1.0)

    def test_mining_mutates_same_state_object(self):
        nebula = PrimordialNebula()
        state = nebula.primordial_nebula_state
        nebula.size = 100.0

        nebula.record_liquid_hydrocarbon_level(100.0)
        nebula.record_liquid_hydrocarbon_level(130.0)
        result = nebula.mine_liquid_hydrocarbons(3.0)

        self.assertIs(nebula.primordial_nebula_state, state)
        self.assertEqual(result, 3.0)
        self.assertEqual(
            state.previous_liquid_hydrocarbon_level,
            100.0,
        )
        self.assertEqual(
            state.current_liquid_hydrocarbon_level,
            127.0,
        )
        self.assertEqual(state.mined_from_current_growth, 3.0)

    def test_tick_mutates_same_state_object(self):
        nebula = PrimordialNebula()
        state = nebula.primordial_nebula_state

        result = nebula.tick()

        self.assertIs(nebula.primordial_nebula_state, state)
        self.assertEqual(result, 1)
        self.assertEqual(state.tick_count, 1)

    def test_public_state_is_deeply_detached_boundary(self):
        nebula = self._nebula_with_elements()

        public_state = nebula.public_state

        self.assertIsInstance(public_state, dict)
        self.assertEqual(
            public_state["name"],
            "primordial_nebula",
        )

        public_state["source_remnants"][0]["name"] = "changed"
        public_state["elemental_potentials"]["hydrogen"] = 999.0

        self.assertEqual(
            nebula.source_remnants[0]["name"],
            "remnant",
        )
        self.assertEqual(
            nebula.elemental_potentials["hydrogen"],
            2.0,
        )

    def test_to_dict_is_deeply_detached_boundary(self):
        state = PrimordialNebulaState(
            source_remnants=[{"name": "remnant"}],
            elemental_potentials={"hydrogen": 1.0},
        )

        snapshot = state.to_dict()
        snapshot["source_remnants"][0]["name"] = "changed"
        snapshot["elemental_potentials"]["hydrogen"] = 999.0

        self.assertEqual(
            state.source_remnants[0]["name"],
            "remnant",
        )
        self.assertEqual(
            state.elemental_potentials["hydrogen"],
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
