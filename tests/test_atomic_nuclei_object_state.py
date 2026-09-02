import unittest

from universe.atomic_nuclei import AtomicNuclei
from universe.nuclear_state import (
    NuclearFormationState,
)
from universe.particles import Particles
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

    def test_world_registry_stores_state_object(
        self
    ):
        universe, process, _ = self._formed_nuclei()

        state = universe.world["nuclear_state"]
        self.assertIsInstance(
            state,
            NuclearFormationState,
        )
        self.assertIs(state, process.nuclear_state)
        self.assertIsInstance(universe.world, dict)

    def test_public_result_remains_dict_boundary(
        self
    ):
        _, _, result = self._formed_nuclei()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["nuclear_state"],
            dict,
        )
        self.assertIsInstance(result["nuclei"], dict)

    def test_public_result_is_deeply_detached(
        self
    ):
        _, process, result = self._formed_nuclei()

        result["nuclear_state"][
            "light_nuclei_formed"
        ] = False
        result["nuclei"][
            "hydrogen_nucleus"
        ]["state"] = "changed"

        self.assertTrue(
            process.nuclear_state.light_nuclei_formed
        )
        self.assertEqual(
            process.nuclei[
                "hydrogen_nucleus"
            ]["state"],
            "formed",
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
