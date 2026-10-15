import unittest

from idea_universe.primordial_stellar_state import (
    PrimordialNebulaRemnant,
    PrimordialStellarEpochResult,
)


class PrimordialStellarRuntimeObjectStateTests(
    unittest.TestCase
):

    def test_remnant_is_object_only(self):
        remnant = PrimordialNebulaRemnant(
            source="primordial_idea_star",
            elemental_potentials={
                "hydrogen": 1.0,
                "carbon": 1.0,
            },
        )

        self.assertEqual(
            remnant.type,
            "primordial_nebula_remnant",
        )

        self.assertEqual(
            remnant.source,
            "primordial_idea_star",
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    remnant,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = remnant[
                "source"
            ]

    def test_remnant_to_dict_is_detached_boundary(self):
        remnant = PrimordialNebulaRemnant(
            source="primordial_idea_star",
            elemental_potentials={
                "hydrogen": 1.0,
            },
        )

        snapshot = (
            remnant.to_dict()
        )

        snapshot[
            "elemental_potentials"
        ][
            "hydrogen"
        ] = 999.0

        self.assertEqual(
            remnant
            .elemental_potentials[
                "hydrogen"
            ],
            1.0,
        )

    def test_stellar_epoch_result_is_object_only(self):
        remnant = PrimordialNebulaRemnant(
            source="primordial_idea_star",
        )

        nebula = object()
        star = object()

        result = PrimordialStellarEpochResult(
            primordial_nebula=nebula,
            stars=[
                star,
            ],
            remnants=[
                remnant,
            ],
        )

        self.assertIs(
            result.primordial_nebula,
            nebula,
        )

        self.assertEqual(
            result.stars,
            (
                star,
            ),
        )

        self.assertEqual(
            result.remnants,
            (
                remnant,
            ),
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
            _ = result[
                "stars"
            ]

    def test_stellar_epoch_result_rejects_mapping_remnant(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            PrimordialStellarEpochResult(
                primordial_nebula=object(),
                stars=[],
                remnants=[
                    {
                        "source":
                            "legacy_remnant",
                    },
                ],
            )


if __name__ == "__main__":
    unittest.main()
