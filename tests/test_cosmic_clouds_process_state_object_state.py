import unittest

from universe.cosmic_clouds import CosmicClouds
from universe.cosmic_clouds_process_state import (
    CosmicCloudsProcessState,
)
from universe.primordial_objects import (
    PrimordialElement,
)
from universe.universe import Universe
from universe.big_bang import BigBang


class CosmicCloudsProcessStateObjectStateTests(
    unittest.TestCase
):

    def _wire_canonical_big_bang(self, universe, elements):
        big_bang = BigBang(universe)
        big_bang.primordial_elements = elements
        universe.big_bang = big_bang

    def _primordial_element(self, name):
        return PrimordialElement(
            name=name,
            state="formed",
            origin="big_bang_nucleosynthesis",
        )

    def test_process_starts_ready_as_enum(self):
        process = CosmicClouds(Universe())

        self.assertIs(
            process.state,
            CosmicCloudsProcessState.READY,
        )
        self.assertEqual(
            process.public_state["state"],
            "ready",
        )

    def test_missing_element_sets_failed_enum(self):
        universe = Universe()
        primordial_elements = {
            "hydrogen": self._primordial_element(
                "hydrogen"
            ),
        }
        self._wire_canonical_big_bang(universe, primordial_elements)

        process = CosmicClouds(universe)

        result = process.form_germinal_clouds()

        self.assertIs(
            process.state,
            CosmicCloudsProcessState.FAILED,
        )
        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FAILED,
        )

    def test_formation_sets_formed_enum(self):
        universe = Universe()
        primordial_elements = {
            "hydrogen": self._primordial_element(
                "hydrogen"
            ),
            "helium": self._primordial_element(
                "helium"
            ),
        }
        self._wire_canonical_big_bang(universe, primordial_elements)

        process = CosmicClouds(universe)

        result = process.form_germinal_clouds()

        self.assertIs(
            process.state,
            CosmicCloudsProcessState.FORMED,
        )
        self.assertIs(
            result.state,
            CosmicCloudsProcessState.FORMED,
        )

    def test_string_state_is_rejected(self):
        process = CosmicClouds(Universe())

        with self.assertRaises(TypeError):
            process.state = "formed"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in CosmicCloudsProcessState
            },
            {
                "ready",
                "failed",
                "formed",
            },
        )


if __name__ == "__main__":
    unittest.main()
