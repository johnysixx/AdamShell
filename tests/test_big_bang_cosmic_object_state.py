import unittest

from universe.big_bang import BigBang
from universe.big_bang_state import (
    BigBangCosmicState,
)
from universe.universe import Universe


class BigBangCosmicObjectStateTests(
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

    def test_cosmic_state_is_object_only(
        self
    ):
        state = BigBangCosmicState()

        self._assert_object_only(
            state,
            "spacetime_expanded",
        )

    def test_initial_values_are_preserved(
        self
    ):
        state = BigBangCosmicState()

        self.assertFalse(state.spacetime_expanded)
        self.assertFalse(
            state.primordial_plasma_formed
        )
        self.assertFalse(
            state.light_nuclei_conditions_prepared
        )
        self.assertFalse(
            state.light_separated_from_darkness
        )
        self.assertTrue(state.darkness_present)

    def test_process_mutates_same_state_object(
        self
    ):
        process = BigBang(Universe())
        state = process.cosmic_state

        process.expand_spacetime()
        process.form_primordial_plasma()
        process.form_light_elements()
        process.separate_light_from_darkness()

        self.assertIs(process.cosmic_state, state)
        self.assertTrue(state.spacetime_expanded)
        self.assertTrue(
            state.primordial_plasma_formed
        )
        self.assertTrue(
            state.light_nuclei_conditions_prepared
        )
        self.assertTrue(
            state.light_separated_from_darkness
        )

    def test_world_registry_stores_state_object(
        self
    ):
        universe = Universe()

        universe.start_big_bang()

        state = universe.world["cosmic_state"]
        self.assertIsInstance(
            state,
            BigBangCosmicState,
        )
        self.assertIs(
            state,
            universe.big_bang.cosmic_state,
        )
        self.assertIsInstance(universe.world, dict)

    def test_public_state_remains_dict_boundary(
        self
    ):
        universe = Universe()

        result = universe.start_big_bang()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(
            result["cosmic_state"],
            dict,
        )
        self.assertIsInstance(
            result["primordial_elements"],
            dict,
        )
        self.assertIsInstance(
            result["phases"],
            list,
        )

    def test_public_snapshot_is_deeply_detached(
        self
    ):
        universe = Universe()
        result = universe.start_big_bang()

        result["cosmic_state"][
            "spacetime_expanded"
        ] = False
        result["primordial_elements"][
            "hydrogen"
        ]["state"] = "changed"
        result["phases"][0][
            "name"
        ] = "changed"

        process = universe.big_bang
        self.assertTrue(
            process.cosmic_state.spacetime_expanded
        )
        self.assertEqual(
            process.primordial_elements[
                "hydrogen"
            ]["state"],
            "formed",
        )
        self.assertEqual(
            process.phases[0]["name"],
            "primordial_void",
        )

    def test_to_dict_is_detached_boundary(
        self
    ):
        state = BigBangCosmicState()
        state.spacetime_expanded = True

        snapshot = state.to_dict()
        snapshot["spacetime_expanded"] = False

        self.assertTrue(state.spacetime_expanded)


if __name__ == "__main__":
    unittest.main()
