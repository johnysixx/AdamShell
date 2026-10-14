import unittest

from universe.aroma_composition import (
    AromaComposition,
)


class AromaCompositionObjectStateTests(
    unittest.TestCase
):

    def assert_object_only(
        self,
        composition,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    composition,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = composition["cat"]

    def test_composition_is_clean_object(
        self,
    ):
        composition = (
            AromaComposition.from_pairs(
                ("cat", 1.0),
                ("fur", 0.8),
            )
        )

        self.assert_object_only(
            composition
        )

        self.assertEqual(
            composition.amount("cat"),
            1.0,
        )

        self.assertEqual(
            composition.amount("missing"),
            0.0,
        )

    def test_scaling_returns_composition(
        self,
    ):
        composition = (
            AromaComposition.from_pairs(
                ("cat", 1.0),
            )
        )

        scaled = composition.scaled(
            0.25
        )

        self.assertIsInstance(
            scaled,
            AromaComposition,
        )

        self.assertEqual(
            scaled.amount("cat"),
            0.25,
        )

        self.assertEqual(
            composition.amount("cat"),
            1.0,
        )

    def test_combining_and_averaging_are_object_operations(
        self,
    ):
        first = (
            AromaComposition.from_pairs(
                ("cat", 1.0),
                ("fur", 0.8),
            )
        )

        second = (
            AromaComposition.from_pairs(
                ("cat", 0.6),
                ("berry", 0.4),
            )
        )

        combined = (
            AromaComposition.combine(
                first,
                second,
            )
        )

        averaged = first.average_with(
            second
        )

        self.assertEqual(
            combined.amount("cat"),
            1.6,
        )

        self.assertAlmostEqual(
            averaged.amount("cat"),
            0.8,
        )

        self.assertAlmostEqual(
            averaged.amount("berry"),
            0.2,
        )

    def test_similarity_is_domain_operation(
        self,
    ):
        first = (
            AromaComposition.from_pairs(
                ("ozone", 1.0),
                ("electrical", 0.75),
            )
        )

        same = (
            AromaComposition.from_pairs(
                ("ozone", 1.0),
                ("electrical", 0.75),
            )
        )

        other = (
            AromaComposition.from_pairs(
                ("berry", 1.0),
            )
        )

        self.assertAlmostEqual(
            first.similarity_to(same),
            1.0,
        )

        self.assertEqual(
            first.similarity_to(other),
            0.0,
        )

    def test_to_dict_is_explicit_detached_boundary(
        self,
    ):
        composition = (
            AromaComposition.from_pairs(
                ("cat", 1.0),
            )
        )

        snapshot = composition.to_dict()

        snapshot["cat"] = 99.0

        self.assertEqual(
            composition.amount("cat"),
            1.0,
        )


if __name__ == "__main__":
    unittest.main()
