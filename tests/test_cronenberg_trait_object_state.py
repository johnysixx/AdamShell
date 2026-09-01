import unittest
from types import SimpleNamespace

from core.entity.cronenberg_system.traits import (
    CronenbergTraits,
    CronenbergTraitValues,
)
from meeting_place.lemonade_profile import (
    LemonadeBatchProfile
)


class ConstantRng:

    def uniform(self, minimum, maximum):
        return 1.0


class CronenbergTraitObjectStateTests(
    unittest.TestCase
):

    def _create_traits(
        self,
        error=None,
        source_component="test",
        source_operation="test",
    ):
        return CronenbergTraits(
            error=error or RuntimeError("test"),
            source_component=source_component,
            source_operation=source_operation,
            rng=ConstantRng(),
        )

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
                callable(
                    getattr(
                        value,
                        mapping_method,
                        None,
                    )
                )
            )

        with self.assertRaises(TypeError):
            _ = value[key]

    def test_trait_state_has_no_mapping_api(
        self
    ):
        traits = self._create_traits()

        self._assert_object_only(
            traits,
            "acidity",
        )
        self.assertIsInstance(
            traits.values,
            CronenbergTraitValues
        )
        self._assert_object_only(
            traits.values,
            "acidity",
        )

    def test_influences_mutate_attribute_values(
        self
    ):
        traits = self._create_traits(
            source_component="cat_geometry",
            source_operation="detour_paradox",
        )
        values = traits.values

        self.assertEqual(values.acidity, 1.0)
        self.assertEqual(values.stability, 0.6)
        self.assertEqual(
            values.dark_energy_affinity,
            1.15
        )
        self.assertEqual(values.viscosity, 1.2)
        self.assertEqual(values.cat_scent, 1.35)
        self.assertEqual(
            values.quantum_coherence,
            1.35
        )

    def test_value_for_replaces_mapping_get(
        self
    ):
        traits = self._create_traits()

        self.assertEqual(
            traits.value_for("acidity"),
            traits.values.acidity
        )
        self.assertEqual(
            traits.value_for(
                "unknown_trait",
                1.25,
            ),
            1.25
        )

    def test_normalization_keeps_same_object(
        self
    ):
        traits = self._create_traits()
        values = traits.values

        values.shift("acidity", 10.0)
        values.shift("sweetness", -10.0)
        values.normalize()

        self.assertIs(traits.values, values)
        self.assertEqual(values.acidity, 2.0)
        self.assertEqual(values.sweetness, 0.1)

    def test_public_state_is_detached_dict(
        self
    ):
        traits = self._create_traits()
        public_state = traits.public_state

        public_state["values"][
            "acidity"
        ] = 99.0
        public_state["birth_influences"][0][
            "amount"
        ] = 99.0

        self.assertEqual(
            traits.values.acidity,
            1.0
        )
        self.assertEqual(
            traits.birth_influences[0][
                "amount"
            ],
            -0.15
        )

    def test_lemonade_profile_reads_object_values(
        self
    ):
        first_traits = self._create_traits()
        second_traits = self._create_traits()
        first_traits.values.acidity = 1.0
        second_traits.values.acidity = 2.0
        first = SimpleNamespace(
            id="first",
            name="first",
            size=1.0,
            traits=first_traits,
            quantum_links=[],
        )
        second = SimpleNamespace(
            id="second",
            name="second",
            size=3.0,
            traits=second_traits,
            quantum_links=[],
        )

        profile = LemonadeBatchProfile().build(
            [first, second]
        )

        self.assertEqual(
            profile["traits"]["acidity"],
            1.75
        )
        self.assertEqual(
            profile["source_mass"],
            4.0
        )


if __name__ == "__main__":
    unittest.main()
