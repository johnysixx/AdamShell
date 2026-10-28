import unittest

from universe.atomic_nuclei import AtomicNuclei
from universe.nuclear_objects import AtomicNucleus
from universe.nuclear_state import (
    NuclearFormationState,
)
from universe.particles import Particles
from universe.physical_formation_result_state import (
    AtomicNucleiFormationResult,
)
from universe.universe import Universe


class AtomicNucleiObjectStateTests(
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

    def _formed_nuclei(self):
        universe = Universe()
        universe.start_big_bang()
        Particles(universe).form_particles()
        process = AtomicNuclei(universe)
        result = process.form_light_nuclei()

        return universe, process, result

    def test_nuclear_state_is_object_only(
        self
    ):
        state = NuclearFormationState()

        self._assert_object_only(
            state,
            "light_nuclei_formed",
        )

    def test_initial_values_are_preserved(
        self
    ):
        state = NuclearFormationState()

        for value in state.to_dict().values():
            self.assertFalse(value)

    def test_formation_mutates_same_state_object(
        self
    ):
        universe = Universe()
        universe.start_big_bang()
        Particles(universe).form_particles()
        process = AtomicNuclei(universe)
        state = process.nuclear_state

        process.form_light_nuclei()

        self.assertIs(process.nuclear_state, state)
        for value in state.to_dict().values():
            self.assertTrue(value)

    def test_world_keeps_snapshot_without_live_nuclear_state(
        self
    ):
        universe, process, _ = self._formed_nuclei()

        state = process.nuclear_state

        self.assertNotIn(
            "nuclear_state",
            universe.world,
        )
        self.assertIsInstance(
            state,
            NuclearFormationState,
        )
        self.assertIs(
            process.result.nuclear_state,
            state,
        )
        self.assertIsInstance(
            universe.world["atomic_nuclei"],
            dict,
        )
        self.assertIsInstance(
            universe.world["atomic_nuclei"][
                "nuclear_state"
            ],
            dict,
        )
        self.assertTrue(
            universe.world["atomic_nuclei"][
                "nuclear_state"
            ]["light_nuclei_formed"]
        )
        self.assertEqual(
            set(
                universe.world["atomic_nuclei"][
                    "nuclei"
                ]
            ),
            set(process.nuclei),
        )
        self.assertIsInstance(universe.world, dict)

    def test_runtime_result_is_object_and_snapshot_is_dict(
        self
    ):
        _, process, result = self._formed_nuclei()

        self.assertIsInstance(
            result,
            AtomicNucleiFormationResult,
        )
        self._assert_object_only(
            result,
            "state",
        )
        self.assertIs(
            result.nuclear_state,
            process.nuclear_state,
        )
        self.assertIs(
            result.nuclei[
                "hydrogen_nucleus"
            ],
            process.nuclei[
                "hydrogen_nucleus"
            ],
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot["nuclear_state"],
            dict,
        )
        self.assertIsInstance(
            snapshot["nuclei"],
            dict,
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_nuclei()

        snapshot = result.to_dict()

        snapshot["nuclear_state"][
            "light_nuclei_formed"
        ] = False
        snapshot["nuclei"][
            "hydrogen_nucleus"
        ]["state"] = "changed"

        self.assertTrue(
            process.nuclear_state.light_nuclei_formed
        )
        self.assertEqual(
            process.nuclei[
                "hydrogen_nucleus"
            ].state,
            "formed",
        )


    def test_nucleus_registry_stores_domain_objects(
        self
    ):
        universe, process, _ = self._formed_nuclei()

        hydrogen = process.nuclei[
            "hydrogen_nucleus"
        ]
        helium = process.nuclei[
            "helium_nucleus"
        ]

        self.assertIsInstance(
            hydrogen,
            AtomicNucleus,
        )
        self.assertIsInstance(
            helium,
            AtomicNucleus,
        )
        self.assertIs(
            universe.world["light_nuclei"][
                "hydrogen_nucleus"
            ],
            hydrogen,
        )

    def test_nucleus_is_object_only(
        self
    ):
        _, process, _ = self._formed_nuclei()

        self._assert_object_only(
            process.nuclei["hydrogen_nucleus"],
            "state",
        )

    def test_nucleus_values_are_attribute_based(
        self
    ):
        _, process, _ = self._formed_nuclei()

        deuterium = process.nuclei[
            "deuterium_nucleus"
        ]
        lithium = process.nuclei[
            "trace_lithium_nucleus"
        ]

        self.assertEqual(
            deuterium.element_name,
            "hydrogen",
        )
        self.assertEqual(deuterium.protons, 1)
        self.assertEqual(deuterium.neutrons, 1)
        self.assertEqual(deuterium.atomic_number, 1)
        self.assertEqual(deuterium.mass_number, 2)
        self.assertEqual(lithium.mass_number, 7)
        self.assertEqual(
            lithium.future_use,
            ("elements", "atoms", "isotopes"),
        )

    def test_nucleus_to_dict_is_detached_boundary(
        self
    ):
        nucleus = AtomicNucleus(
            name="helium_nucleus",
            element_name="helium",
            protons=2,
            neutrons=2,
        )

        snapshot = nucleus.to_dict()
        snapshot["state"] = "changed"
        snapshot["future_use"].append("changed")

        self.assertEqual(nucleus.state, "formed")
        self.assertNotIn(
            "changed",
            nucleus.future_use,
        )

    def test_nucleus_rejects_invalid_counts(
        self
    ):
        with self.assertRaises(TypeError):
            AtomicNucleus(
                name="invalid",
                element_name="invalid",
                protons={"count": 1},
                neutrons=0,
            )

        with self.assertRaises(ValueError):
            AtomicNucleus(
                name="invalid",
                element_name="invalid",
                protons=1,
                neutrons=-1,
            )

    def test_formation_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        universe.start_big_bang()
        Particles(universe).form_particles()
        process = AtomicNuclei(universe)

        def broken_nucleus(*args, **kwargs):
            raise RuntimeError(
                "nuclear formation exploded"
            )

        process.add_nucleus = broken_nucleus

        result = process.form_light_nuclei()
        cronenberg = result.cronenberg

        self.assertEqual(
            result.type,
            "quantum_error",
        )
        self.assertIn(
            cronenberg,
            universe.cronenbergs,
        )
        self.assertEqual(
            cronenberg.origin.source_component,
            "atomic_nuclei",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_light_nuclei",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "nuclear formation exploded",
        )

    def test_to_dict_is_detached_boundary(
        self
    ):
        state = NuclearFormationState()
        state.light_nuclei_formed = True

        snapshot = state.to_dict()
        snapshot["light_nuclei_formed"] = False

        self.assertTrue(state.light_nuclei_formed)


if __name__ == "__main__":
    unittest.main()
