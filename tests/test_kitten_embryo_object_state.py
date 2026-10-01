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

    def test_boundary_is_detached(
        self
    ):
        embryo = self._embryo()

        boundary = (
            embryo.to_dict()
        )

        self.assertIsInstance(
            boundary,
            dict,
        )

        self.assertIsInstance(
            boundary[
                "profile"
            ],
            dict,
        )

        self.assertIsInstance(
            boundary[
                "viability"
            ],
            dict,
        )

        boundary[
            "profile"
        ][
            "color"
        ] = "white"

        boundary[
            "phenotype"
        ][
            "profile"
        ][
            "color"
        ] = "white"

        boundary[
            "special_traits"
        ].append(
            "changed"
        )

        self.assertEqual(
            embryo.profile.color,
            "black",
        )

        self.assertEqual(
            embryo
            .phenotype
            .profile
            .color,
            "black",
        )

        self.assertEqual(
            tuple(
                embryo.special_traits
            ),
            (),
        )

    def test_reproduction_boundary_serializes_embryo(
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

        boundary = (
            state.to_dict()
        )

        self.assertIs(
            state.embryos[0],
            embryo,
        )

        self.assertIsInstance(
            boundary[
                "embryos"
            ][0],
            dict,
        )

        self.assertEqual(
            boundary[
                "embryos"
            ][0][
                "id"
            ],
            embryo.id,
        )

        boundary[
            "embryos"
        ][0][
            "profile"
        ][
            "color"
        ] = "changed"

        self.assertEqual(
            embryo.profile.color,
            "black",
        )


if __name__ == "__main__":
    unittest.main()
