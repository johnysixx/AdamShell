import unittest
from dataclasses import replace

from universe.big_bang import BigBang
from universe.big_bang_state import (
    BigBangCosmicState,
    BigBangRunResult,
)
from universe.primordial_objects import (
    PrimordialEnergy,
    PrimordialMatter,
    PrimordialElement,
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

    def test_runtime_result_is_object_and_public_snapshot_is_dict(
        self
    ):
        universe = Universe()

        result = universe.start_big_bang()

        self.assertIsInstance(
            result,
            BigBangRunResult,
        )
        self.assertIs(
            result.cosmic_state,
            universe.big_bang.cosmic_state,
        )
        self.assertIs(
            result.phases[0],
            universe.big_bang.phases[0],
        )
        self.assertIs(
            result.primordial_elements[
                "hydrogen"
            ],
            universe.big_bang
            .primordial_elements[
                "hydrogen"
            ],
        )

        self.assertIs(
            result.primordial_components["energy"],
            universe.big_bang.primordial_components["energy"],
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result["cosmic_state"]

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot,
            dict,
        )
        self.assertIsInstance(
            snapshot["cosmic_state"],
            dict,
        )
        self.assertIsInstance(
            snapshot["primordial_elements"],
            dict,
        )
        self.assertIsInstance(
            snapshot["primordial_components"],
            dict,
        )
        self.assertIsInstance(
            snapshot["phases"],
            list,
        )

        self.assertIsInstance(
            universe.big_bang.public_state,
            dict,
        )

    def test_public_snapshot_is_deeply_detached(
        self
    ):
        universe = Universe()
        result = universe.start_big_bang()

        snapshot = result.to_dict()

        snapshot["cosmic_state"][
            "spacetime_expanded"
        ] = False
        snapshot["primordial_components"]["energy"]["state"] = "changed"
        snapshot["primordial_elements"][
            "hydrogen"
        ]["state"] = "changed"
        snapshot["phases"][0][
            "name"
        ] = "changed"

        process = universe.big_bang
        self.assertTrue(
            process.cosmic_state.spacetime_expanded
        )
        self.assertEqual(
            process.primordial_components["energy"].state,
            "released",
        )
        self.assertEqual(
            process.primordial_elements[
                "hydrogen"
            ].state,
            "formed",
        )
        self.assertEqual(
            process.phases[0].name,
            "primordial_void",
        )

    def test_primordial_registry_contains_component_objects(self):
        universe = Universe()
        universe.start_big_bang()

        self.assertNotIn("primordial_elements", universe.world)
        components = universe.big_bang.primordial_components
        elements = universe.big_bang.primordial_elements

        self.assertEqual(set(components), {"energy", "matter"})
        self.assertEqual(
            set(elements),
            {"hydrogen", "helium", "trace_lithium"},
        )

        for element in elements.values():
            self.assertIsInstance(
                element,
                PrimordialElement,
            )
            self.assertEqual(element.type, "element")

        self.assertIsInstance(
            components["energy"],
            PrimordialEnergy,
        )
        self.assertIsInstance(
            components["matter"],
            PrimordialMatter,
        )

        self.assertEqual(
            components["energy"].type,
            "primordial_energy",
        )
        self.assertEqual(
            components["matter"].state,
            "forming",
        )
        self.assertEqual(
            elements["hydrogen"].type,
            "element",
        )
        self.assertEqual(
            elements["hydrogen"].origin,
            "big_bang_nucleosynthesis",
        )

    def test_primordial_components_are_object_only(self):
        universe = Universe()
        universe.start_big_bang()

        hydrogen = universe.big_bang.primordial_elements["hydrogen"]

        self._assert_object_only(
            hydrogen,
            "state",
        )

    def test_public_primordial_snapshot_is_detached_dict(self):
        universe = Universe()
        result = universe.start_big_bang()

        hydrogen = universe.big_bang.primordial_elements["hydrogen"]

        self.assertIs(
            result.primordial_elements[
                "hydrogen"
            ],
            hydrogen,
        )

        snapshot = result.to_dict()

        self.assertIsInstance(
            snapshot[
                "primordial_elements"
            ]["hydrogen"],
            dict,
        )

        snapshot[
            "primordial_elements"
        ]["hydrogen"]["state"] = "changed"

        self.assertEqual(
            hydrogen.state,
            "formed",
        )

    def test_result_rejects_cross_domain_components(self):
        result = Universe().start_big_bang()

        with self.assertRaisesRegex(
            TypeError,
            "primordial_elements",
        ):
            replace(
                result,
                primordial_elements={
                    "energy": result.primordial_components["energy"],
                },
            )

        with self.assertRaisesRegex(
            TypeError,
            "primordial_components",
        ):
            replace(
                result,
                primordial_components={
                    "hydrogen": result.primordial_elements["hydrogen"],
                },
            )

        with self.assertRaises(TypeError):
            result.primordial_elements["energy"] = (
                result.primordial_components["energy"]
            )

    def test_domain_types_cannot_be_relabelled(self):
        with self.assertRaises(TypeError):
            PrimordialElement(
                name="hydrogen",
                state="formed",
                type="primordial_energy",
            )

        with self.assertRaises(TypeError):
            PrimordialEnergy(name="hydrogen")

        with self.assertRaises(TypeError):
            PrimordialMatter(name="hydrogen")

    def test_repeated_start_returns_same_runtime_result(
        self
    ):
        universe = Universe()

        first = universe.start_big_bang()
        second = universe.start_big_bang()

        self.assertIs(
            second,
            first,
        )
        self.assertIs(
            second,
            universe.big_bang.result,
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
