import unittest

from universe.atomic_nuclei import AtomicNuclei
from universe.particle_state import (
    ParticleFormationState,
)
from universe.particles import Particles
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

    def test_world_registry_stores_state_object(
        self
    ):
        universe, process, _ = (
            self._formed_particles()
        )

        state = universe.world["particle_state"]
        self.assertIsInstance(
            state,
            ParticleFormationState,
        )
        self.assertIs(state, process.particle_state)
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._formed_particles()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["particle_state"],
            dict,
        )
        self.assertIsInstance(
            result["elementary_particles"],
            dict,
        )
        self.assertIsInstance(
            result["interactions"],
            dict,
        )

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_particles()

        result["particle_state"][
            "nucleons_formed"
        ] = False
        result["elementary_particles"][
            "up_quark"
        ]["state"] = "changed"
        result["interactions"][
            "strong_interaction"
        ]["effect"] = "changed"

        self.assertTrue(
            process.particle_state.nucleons_formed
        )
        self.assertEqual(
            process.elementary_particles[
                "up_quark"
            ]["state"],
            "available",
        )
        self.assertNotEqual(
            process.interactions[
                "strong_interaction"
            ]["effect"],
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
        universe, _, _ = self._formed_particles()
        nuclei = AtomicNuclei(universe)

        result = nuclei.form_light_nuclei()

        self.assertEqual(result["state"], "formed")
        self.assertIn(
            "hydrogen_nucleus",
            nuclei.nuclei,
        )
        self.assertTrue(
            universe.world[
                "particle_state"
            ].nucleons_formed
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
