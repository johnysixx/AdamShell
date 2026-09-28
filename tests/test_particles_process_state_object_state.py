import unittest

from universe.particles import Particles
from universe.particles_process_state import (
    ParticlesProcessState,
)
from universe.universe import Universe


class ParticlesProcessStateObjectStateTests(
    unittest.TestCase
):

    def test_process_starts_ready_as_enum(self):
        process = Particles(Universe())

        self.assertIs(
            process.state,
            ParticlesProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_formation_sets_formed_enum(self):
        process = Particles(Universe())

        result = process.form_particles()

        self.assertIs(
            process.state,
            ParticlesProcessState.FORMED,
        )
        self.assertEqual(
            result["state"],
            "formed",
        )

    def test_string_state_is_rejected(self):
        process = Particles(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in ParticlesProcessState
            },
            {
                "ready",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
