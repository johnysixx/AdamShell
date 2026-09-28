import unittest

from universe.universe import Universe
from universe.universe_lifecycle_state import (
    UniverseLifecycleState,
)


class UniverseLifecycleStateObjectStateTests(
    unittest.TestCase
):

    def test_universe_starts_pre_universe_as_enum(
        self
    ):
        universe = Universe()

        self.assertIs(
            universe.state,
            UniverseLifecycleState.PRE_UNIVERSE,
        )

    def test_big_bang_enters_physical_universe(
        self
    ):
        universe = Universe()

        universe.start_big_bang()

        self.assertIs(
            universe.state,
            UniverseLifecycleState.PHYSICAL_UNIVERSE,
        )

    def test_repeated_big_bang_preserves_physical_state(
        self
    ):
        universe = Universe()
        universe.start_big_bang()

        universe.start_big_bang()

        self.assertIs(
            universe.state,
            UniverseLifecycleState.PHYSICAL_UNIVERSE,
        )

    def test_string_state_is_rejected(self):
        universe = Universe()

        with self.assertRaises(TypeError):
            universe.state = "physical_universe"

    def test_state_values_define_boundary_names(
        self
    ):
        self.assertEqual(
            {
                state.value
                for state in UniverseLifecycleState
            },
            {
                "pre_universe",
                "physical_universe",
            },
        )


if __name__ == "__main__":
    unittest.main()
