import unittest

from universe.atomic_nuclei import AtomicNuclei
from universe.atomic_nuclei_process_state import (
    AtomicNucleiProcessState,
)
from universe.particles import Particles
from universe.universe import Universe


class AtomicNucleiProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = AtomicNuclei(Universe())

        self.assertIs(
            process.state,
            AtomicNucleiProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_formation_sets_formed_enum(self):
        universe = Universe()
        universe.start_big_bang()
        Particles(universe).form_particles()
        process = AtomicNuclei(universe)

        result = process.form_light_nuclei()

        self.assertIs(
            process.state,
            AtomicNucleiProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = AtomicNuclei(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in AtomicNucleiProcessState
            },
            {
                "ready",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
