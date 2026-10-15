import unittest

from idea_universe.primordial_nebula import (
    PrimordialNebula,
)
from idea_universe.primordial_nebula_state import (
    PrimordialNebulaState,
)
from idea_universe.primordial_stellar_state import (
    PrimordialNebulaRemnant,
)


class PrimordialNebulaObjectStateTests(
    unittest.TestCase
):

    def _remnant(self):
        return PrimordialNebulaRemnant(
            source="test_remnant",
            elemental_potentials={
                "hydrogen": 2.0,
                "carbon": 1.0,
            },
        )

    def _nebula_with_elements(self):
        return PrimordialNebula(
            source_remnants=[
                self._remnant(),
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
                hasattr(
                    state,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = state[
                "size"
            ]

    def test_initial_values_are_preserved(self):
        nebula = PrimordialNebula()

        state = (
            nebula
            .primordial_nebula_state
        )

        self.assertIs(
            nebula.state,
            state,
        )

        self.assertEqual(
            state.tick_count,
            0,
        )

        self.assertEqual(
            state.size,
            0.0,
        )

        self.assertEqual(
            state.stars,
            [],
        )

        self.assertEqual(
            state.source_remnants,
            [],
        )

        self.assertEqual(
            state.source_remnant_count,
            0,
        )

        self.assertEqual(
            state.elemental_potentials,
            {},
        )

        self.assertIsNone(
            state
            .previous_liquid_hydrocarbon_level
        )

        self.assertEqual(
            state
            .current_liquid_hydrocarbon_level,
            0.0,
        )

        self.assertEqual(
            state.mined_from_current_growth,
            0.0,
        )

    def test_remnants_are_objects_in_state(self):
        remnant = self._remnant()

        nebula = PrimordialNebula(
            source_remnants=[
                remnant,
            ],
        )

        state = (
            nebula
            .primordial_nebula_state
        )

        self.assertEqual(
            state.source_remnant_count,
            1,
        )

        self.assertIs(
            state.source_remnants[0],
            remnant,
        )

        self.assertIsInstance(
            state.source_remnants[0],
            PrimordialNebulaRemnant,
        )

        self.assertIs(
            nebula.source_remnants,
            state.source_remnants,
        )

        self.assertEqual(
            state.elemental_potentials,
            {
                "hydrogen": 2.0,
                "carbon": 1.0,
            },
        )

    def test_mapping_remnants_are_rejected(self):
        with self.assertRaises(
            TypeError
        ):
            PrimordialNebula(
                source_remnants=[
                    {
                        "source":
                            "legacy_remnant",
                    },
                ],
            )

        with self.assertRaises(
            TypeError
        ):
            PrimordialNebulaState(
                source_remnants=[
                    {
                        "source":
                            "legacy_remnant",
                    },
                ],
            )

    def test_scalar_interface_mutates_same_state_object(
        self
    ):
        nebula = PrimordialNebula()

        state = (
            nebula
            .primordial_nebula_state
        )

        nebula.size = 100.0
        nebula.tick_count = 4

        nebula.current_liquid_hydrocarbon_level = (
            20.0
        )

        self.assertIs(
            nebula.primordial_nebula_state,
            state,
        )

        self.assertEqual(
            state.size,
            100.0,
        )

        self.assertEqual(
            state.tick_count,
            4,
        )

        self.assertEqual(
            state
            .current_liquid_hydrocarbon_level,
            20.0,
        )

    def test_hydrocarbon_formation_mutates_same_state(
        self
    ):
        nebula = (
            self
            ._nebula_with_elements()
        )

        state = (
            nebula
            .primordial_nebula_state
        )

        potentials = (
            state
            .elemental_potentials
        )

        amount = (
            nebula
            .form_hydrocarbons()
        )

        nebula.size = 10.0

        liquid_amount = (
            nebula
            .form_liquid_hydrocarbons()
        )

        self.assertIs(
            nebula.primordial_nebula_state,
            state,
        )

        self.assertIs(
            state.elemental_potentials,
            potentials,
        )

        self.assertEqual(
            amount,
            1.0,
        )

        self.assertEqual(
            liquid_amount,
            1.0,
        )

        self.assertEqual(
            potentials[
                "hydrocarbons"
            ],
            1.0,
        )

        self.assertEqual(
            potentials[
                "liquid_hydrocarbons"
            ],
            1.0,
        )

    def test_mining_mutates_same_state_object(self):
        nebula = PrimordialNebula()

        state = (
            nebula
            .primordial_nebula_state
        )

        nebula.size = 100.0

        nebula.record_liquid_hydrocarbon_level(
            100.0
        )

        nebula.record_liquid_hydrocarbon_level(
            130.0
        )

        result = (
            nebula
            .mine_liquid_hydrocarbons(
                3.0
            )
        )

        self.assertIs(
            nebula.primordial_nebula_state,
            state,
        )

        self.assertEqual(
            result,
            3.0,
        )

        self.assertEqual(
            state
            .previous_liquid_hydrocarbon_level,
            100.0,
        )

        self.assertEqual(
            state
            .current_liquid_hydrocarbon_level,
            127.0,
        )

        self.assertEqual(
            state.mined_from_current_growth,
            3.0,
        )

    def test_tick_mutates_same_state_object(self):
        nebula = PrimordialNebula()

        state = (
            nebula
            .primordial_nebula_state
        )

        result = (
            nebula.tick()
        )

        self.assertIs(
            nebula.primordial_nebula_state,
            state,
        )

        self.assertEqual(
            result,
            1,
        )

        self.assertEqual(
            state.tick_count,
            1,
        )

    def test_public_state_is_deeply_detached_boundary(
        self
    ):
        nebula = (
            self
            ._nebula_with_elements()
        )

        public_state = (
            nebula.public_state
        )

        self.assertIsInstance(
            public_state,
            dict,
        )

        public_state[
            "source_remnants"
        ][0][
            "source"
        ] = "changed"

        public_state[
            "source_remnants"
        ][0][
            "elemental_potentials"
        ][
            "hydrogen"
        ] = 999.0

        public_state[
            "elemental_potentials"
        ][
            "hydrogen"
        ] = 999.0

        self.assertEqual(
            nebula
            .source_remnants[0]
            .source,
            "test_remnant",
        )

        self.assertEqual(
            nebula
            .source_remnants[0]
            .elemental_potentials[
                "hydrogen"
            ],
            2.0,
        )

        self.assertEqual(
            nebula
            .elemental_potentials[
                "hydrogen"
            ],
            2.0,
        )

    def test_to_dict_is_deeply_detached_boundary(
        self
    ):
        remnant = self._remnant()

        state = PrimordialNebulaState(
            source_remnants=[
                remnant,
            ],
            elemental_potentials={
                "hydrogen": 1.0,
            },
        )

        snapshot = (
            state.to_dict()
        )

        snapshot[
            "source_remnants"
        ][0][
            "source"
        ] = "changed"

        snapshot[
            "source_remnants"
        ][0][
            "elemental_potentials"
        ][
            "hydrogen"
        ] = 999.0

        snapshot[
            "elemental_potentials"
        ][
            "hydrogen"
        ] = 999.0

        self.assertEqual(
            state
            .source_remnants[0]
            .source,
            "test_remnant",
        )

        self.assertEqual(
            state
            .source_remnants[0]
            .elemental_potentials[
                "hydrogen"
            ],
            2.0,
        )

        self.assertEqual(
            state
            .elemental_potentials[
                "hydrogen"
            ],
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
