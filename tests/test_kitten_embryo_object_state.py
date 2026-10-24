import unittest

from cats.cat_birth_objects import (
    CatBirthProfile,
    CatPhenotypeResult,
    KittenEmbryo,
)

from cats.cat_reproduction_state import (
    CatReproductionState,
)

from cats.genotype import (
    CatGenotype,
)

from cats.kitten_viability_resolver import (
    KittenGeneticViabilityResult,
)


class KittenEmbryoObjectStateTests(
    unittest.TestCase
):

    def _embryo(self):
        genotype = (
            CatGenotype.create_founder(
                sex="female"
            )
        )

        profile = CatBirthProfile(
            color="black",
            fur_length="short",
            pattern="solid",
            eye_color="green",
            sex="female",
        )

        viability = (
            KittenGeneticViabilityResult(
                status="standard",
                viable=True,
                rare=False,
                reason=None,
                details=None,
                special_traits=(),
                genotype=genotype,
            )
        )

        phenotype = CatPhenotypeResult(
            profile=profile,
            base_color="black",
            diluted=False,
            white_spotted=False,
            colorpoint=False,
            genotype=genotype,
        )

        return KittenEmbryo(
            id="embryo_0001",
            mother_name="mother",
            father_name="father",
            genotype=genotype,
            phenotype=phenotype,
            profile=profile,
            viability=viability,
            genetic_status="standard",
            rare=False,
            special_traits=(),
        )

    def test_embryo_has_no_mapping_api(
        self
    ):
        embryo = self._embryo()

        self.assertEqual(
            embryo.id,
            "embryo_0001",
        )

        self.assertEqual(
            embryo.state,
            "gestating",
        )

        self.assertEqual(
            embryo.type,
            "kitten_embryo",
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    embryo,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = embryo[
                "id"
            ]

    def test_embryo_contains_typed_profile_and_viability(
        self
    ):
        embryo = self._embryo()

        self.assertIsInstance(
            embryo.profile,
            CatBirthProfile,
        )

        self.assertIsInstance(
            embryo.viability,
            KittenGeneticViabilityResult,
        )

        self.assertIsInstance(
            embryo.phenotype,
            CatPhenotypeResult,
        )

        self.assertIs(
            embryo.profile,
            embryo.phenotype.profile,
        )

        self.assertEqual(
            embryo.profile.color,
            "black",
        )

        self.assertEqual(
            embryo.viability.status,
            "standard",
        )

    def test_reproduction_state_preserves_embryo_object_graph(
        self
    ):
        embryo = self._embryo()

        state = CatReproductionState(
            sex="female"
        )

        state.embryos.append(
            embryo
        )

        stored = (
            state.embryos[0]
        )

        self.assertIs(
            stored,
            embryo,
        )

        self.assertIs(
            stored.profile,
            embryo.profile,
        )

        self.assertIs(
            stored.phenotype,
            embryo.phenotype,
        )

        self.assertIs(
            stored.viability,
            embryo.viability,
        )

        self.assertFalse(
            hasattr(
                state,
                "to_dict",
            )
        )

    def test_reproduction_state_keeps_embryo_values(
        self
    ):
        embryo = self._embryo()

        state = (
            CatReproductionState(
                sex="female"
            )
        )

        state.embryos.append(
            embryo
        )

        self.assertIs(
            state.embryos[0],
            embryo,
        )

        self.assertEqual(
            state.embryos[0].id,
            "embryo_0001",
        )

        self.assertEqual(
            state.embryos[0].profile.color,
            "black",
        )

        self.assertEqual(
            state.embryos[0].viability.status,
            "standard",
        )

        self.assertEqual(
            state.embryos[0].special_traits,
            (),
        )

        self.assertFalse(
            hasattr(
                state,
                "to_dict",
            )
        )


if __name__ == "__main__":
    unittest.main()
