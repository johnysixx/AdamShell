import unittest

from cats.cat_birth_objects import (
    CatKittenBirthResult,
    CatLitter,
    CatLitterBirthResult,
)

from cats.cat_reproduction_state import (
    CatReproductionState,
)


class CatLitterObjectStateTests(
    unittest.TestCase
):

    def _birth_result(self):
        return (
            CatKittenBirthResult(
                embryo_id=(
                    "embryo_0001"
                ),
                kitten="kitten_0001",
                father="father",
                genetic_status="viable",
                rare=False,
                born=True,
            )
        )

    def _litter(self):
        return (
            CatLitter(
                litter_number=1,
                mother="mother",
                father_names=(
                    "father",
                ),
                embryos_present=1,
                kittens_born=1,
                kitten_names=(
                    "kitten_0001",
                ),
                birth_results=(
                    self._birth_result(),
                ),
                pregnancy_day=63,
                gestation_days=63,
                birth_day=74,
            )
        )

    def test_birth_result_has_no_mapping_api(
        self
    ):
        result = (
            self._birth_result()
        )

        self.assertEqual(
            result.embryo_id,
            "embryo_0001",
        )

        self.assertTrue(
            result.born
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
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "embryo_id"
            ]

    def test_litter_contains_only_typed_birth_results(
        self
    ):
        litter = self._litter()

        self.assertIsInstance(
            litter.birth_results[0],
            CatKittenBirthResult,
        )

        self.assertEqual(
            litter.father_names,
            (
                "father",
            ),
        )

        self.assertFalse(
            litter.multiple_sires
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
                    litter,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = litter[
                "kitten_names"
            ]

    def test_litter_rejects_mapping_birth_result(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            CatLitter(
                litter_number=1,
                mother="mother",
                father_names=(
                    "father",
                ),
                embryos_present=1,
                kittens_born=1,
                kitten_names=(
                    "kitten_0001",
                ),
                birth_results=(
                    {
                        "embryo_id": (
                            "embryo_0001"
                        ),
                        "born": True,
                    },
                ),
                pregnancy_day=63,
                gestation_days=63,
                birth_day=74,
            )

    def test_litter_birth_result_uses_object_state(
        self
    ):
        litter = self._litter()

        kitten = type(
            "FakeKitten",
            (),
            {
                "name": "kitten_0001",
            },
        )()

        result = (
            CatLitterBirthResult(
                litter=litter,
                kittens=(
                    kitten,
                ),
            )
        )

        self.assertIs(
            result.litter,
            litter,
        )

        self.assertIs(
            result.kittens[0],
            kitten,
        )

        self.assertTrue(
            result.born
        )

        self.assertEqual(
            result.kitten_names,
            (
                "kitten_0001",
            ),
        )

        self.assertFalse(
            result.multiple_sires
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
                    result,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = result[
                "kittens"
            ]

        self.assertEqual(
            litter.kitten_names,
            (
                "kitten_0001",
            ),
        )


if __name__ == "__main__":
    unittest.main()
