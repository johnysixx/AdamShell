import unittest

from universe.atomic_nuclei import AtomicNuclei
from universe.particle_state import (
    ParticleFormationState,
)
from universe.particles import Particles
from universe.atomic_nuclei_process_state import (
    AtomicNucleiProcessState,
)
from universe.physical_formation_result_state import (
    AtomicNucleiFormationResult,
    ParticleFormationResult,
)
from universe.universe import Universe


class ParticleFormationObjectStateTests(
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

    def _formed_particles(self):
        universe = Universe()
        universe.start_big_bang()
        process = Particles(universe)
        result = process.form_particles()

        return universe, process, result

    def test_particle_state_is_object_only(
        self
    ):
        state = ParticleFormationState()

        self._assert_object_only(
            state,
            "nucleons_formed",
        )

    def test_initial_values_are_preserved(
        self
    ):
        state = ParticleFormationState()

        for value in state.to_dict().values():
            self.assertFalse(value)

    def test_formation_mutates_same_state_object(
        self
    ):
        universe = Universe()
        universe.start_big_bang()
        process = Particles(universe)
        state = process.particle_state

        process.form_particles()

        self.assertIs(process.particle_state, state)
        for value in state.to_dict().values():
            self.assertTrue(value)

    def test_world_keeps_snapshot_without_live_particle_state(
        self
    ):
        universe, process, _ = (
            self._formed_particles()
        )

        state = process.particle_state
        result = process.result

        self.assertNotIn(
            "particle_state",
            universe.world,
        )
        self.assertIsInstance(
            state,
            ParticleFormationState,
        )
        self.assertIs(
            result.particle_state,
            state,
        )

        public_state = universe.world["particles"]

        self.assertIsInstance(
            public_state,
            dict,
        )
        self.assertIsInstance(
            public_state["particle_state"],
            dict,
        )
        self.assertEqual(
            public_state["particle_state"],
            state.to_dict(),
        )

        self.assertTrue(
            state.nucleons_formed,
        )

        for name in (
            "elementary_particles",
            "composite_particles",
            "fields",
            "interactions",
        ):
            self.assertIsInstance(
                public_state[name],
                dict,
            )

        self.assertIs(
            universe.world["elementary_particles"],
            process.elementary_particles,
        )
        self.assertIs(
            universe.world["composite_particles"],
            process.composite_particles,
        )
        self.assertIs(
            universe.world["particle_fields"],
            process.fields,
        )
        self.assertIs(
            universe.world["particle_interactions"],
            process.interactions,
        )

        self.assertIs(
            universe.world["nucleons"]["proton"],
            process.composite_particles["proton"],
        )
        self.assertIs(
            universe.world["nucleons"]["neutron"],
            process.composite_particles["neutron"],
        )

        # Mutating the public snapshot must not
        # change the canonical runtime state.

        public_state["particle_state"][
            "nucleons_formed"
        ] = False

        self.assertTrue(
            state.nucleons_formed,
        )
        self.assertTrue(
            result.particle_state.nucleons_formed,
        )

        self.assertIsInstance(universe.world, dict)

    def test_runtime_result_is_object_and_snapshot_is_dict(
        self
    ):
        _, process, result = self._formed_particles()

        self.assertIsInstance(
            result,
            ParticleFormationResult,
        )
        self._assert_object_only(
            result,
            "state",
        )

        self.assertIs(
            result.particle_state,
            process.particle_state,
        )
        self.assertIs(
            result.elementary_particles[
                "up_quark"
            ],
            process.elementary_particles[
                "up_quark"
            ],
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot,
            dict,
        )
        self.assertIsInstance(
            snapshot["particle_state"],
            dict,
        )
        self.assertIsInstance(
            snapshot["elementary_particles"],
            dict,
        )
        self.assertIsInstance(
            snapshot["interactions"],
            dict,
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_particles()

        snapshot = result.to_dict()

        snapshot["particle_state"][
            "nucleons_formed"
        ] = False
        snapshot["elementary_particles"][
            "up_quark"
        ]["state"] = "changed"
        snapshot["interactions"][
            "strong_interaction"
        ]["effect"] = "changed"

        self.assertTrue(
            process.particle_state.nucleons_formed
        )
        self.assertEqual(
            process.elementary_particles[
                "up_quark"
            ].state,
            "available",
        )
        self.assertNotEqual(
            process.interactions[
                "strong_interaction"
            ].effect,
            "changed",
        )

    def test_formation_error_creates_cronenberg(
        self
    ):
        universe = Universe()
        universe.start_big_bang()
        process = Particles(universe)

        def broken_quark_formation():
            raise RuntimeError(
                "particle formation exploded"
            )

        process.form_quarks = broken_quark_formation

        result = process.form_particles()
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
            "particles",
        )
        self.assertEqual(
            cronenberg.origin.source_operation,
            "form_particles",
        )
        self.assertEqual(
            cronenberg.origin.error_type,
            "RuntimeError",
        )
        self.assertEqual(
            cronenberg.origin.error_message,
            "particle formation exploded",
        )

    def test_atomic_nuclei_consume_object_state(
        self
    ):
        universe, particles, particle_result = (
            self._formed_particles()
        )
        nuclei = AtomicNuclei(universe)

        result = nuclei.form_light_nuclei()

        self.assertIsInstance(
            result,
            AtomicNucleiFormationResult,
        )
        self.assertIs(
            result.state,
            AtomicNucleiProcessState.FORMED,
        )
        self.assertIn(
            "hydrogen_nucleus",
            nuclei.nuclei,
        )
        self.assertIs(
            particle_result.particle_state,
            particles.particle_state,
        )
        self.assertTrue(
            particles.particle_state.nucleons_formed,
        )
        self.assertNotIn(
            "particle_state",
            universe.world,
        )

    def test_to_dict_is_detached_boundary(
        self
    ):
        state = ParticleFormationState()
        state.nucleons_formed = True

        snapshot = state.to_dict()
        snapshot["nucleons_formed"] = False

        self.assertTrue(state.nucleons_formed)


if __name__ == "__main__":
    unittest.main()
