import unittest
from dataclasses import FrozenInstanceError

from cats.cat_trait_dice_mapping import (
    CatTraitDieAssignment,
    CatTraitDiceMapping,
    CatTraitDiceMappingResult,
)


class CatTraitDiceMappingObjectStateTests(unittest.TestCase):

    def test_resolve_returns_mapping_result_object(self):
        result = CatTraitDiceMapping().resolve(7)

        self.assertIsInstance(
            result,
            CatTraitDiceMappingResult,
        )
        self.assertEqual(result.cat_d20_value, 7)
        self.assertTrue(result.resolved)
        self.assertEqual(
            result.name,
            "cat_trait_dice_mapping_resolved",
        )
        self.assertEqual(
            {item.die for item in result.assignments},
            set(CatTraitDiceMapping.DICE),
        )

    def test_inverse_trait_mapping_is_available_through_methods(self):
        result = CatTraitDiceMapping().resolve(3)

        for assignment in result.assignments:
            self.assertEqual(
                result.trait_for_die(assignment.die),
                assignment.trait,
            )
            self.assertEqual(
                result.die_for_trait(assignment.trait),
                assignment.die,
            )

    def test_result_has_no_mapping_compatibility(self):
        result = CatTraitDiceMapping().resolve(1)

        with self.assertRaises(TypeError):
            _ = result["assignments"]

        with self.assertRaises(AttributeError):
            result.get("assignments")

        self.assertFalse(hasattr(result, "die_to_trait"))
        self.assertFalse(hasattr(result, "trait_to_die"))

    def test_result_has_no_serialization_shim(self):
        result = CatTraitDiceMapping().resolve(1)

        self.assertFalse(hasattr(result, "to_dict"))

        self.assertEqual(
            result.assignments[0].die,
            "d4",
        )
        self.assertEqual(
            result.trait_for_die("d4"),
            result.assignments[0].trait,
        )

    def test_constructor_requires_typed_assignments(self):
        assignment = CatTraitDieAssignment(
            die="d4",
            trait="color",
        )

        result = CatTraitDiceMappingResult(
            cat_d20_value=1,
            permutation_index=0,
            assignments=(assignment,),
        )

        self.assertIs(result.assignments[0], assignment)
        self.assertEqual(result.trait_for_die("d4"), "color")
        self.assertEqual(result.die_for_trait("color"), "d4")

        with self.assertRaises(TypeError):
            CatTraitDiceMappingResult(
                cat_d20_value=1,
                permutation_index=0,
                assignments={"d4": "color"},
            )

        with self.assertRaises(TypeError):
            CatTraitDiceMappingResult(
                cat_d20_value=1,
                permutation_index=0,
                assignments=[assignment],
            )

        with self.assertRaises(TypeError):
            CatTraitDiceMappingResult(
                cat_d20_value=1,
                permutation_index=0,
                assignments=(
                    {"die": "d4", "trait": "color"},
                ),
            )

    def test_duplicate_assignments_are_rejected(self):
        with self.assertRaises(ValueError):
            CatTraitDiceMappingResult(
                cat_d20_value=1,
                permutation_index=0,
                assignments=(
                    CatTraitDieAssignment("d4", "color"),
                    CatTraitDieAssignment("d4", "pattern"),
                ),
            )

        with self.assertRaises(ValueError):
            CatTraitDiceMappingResult(
                cat_d20_value=1,
                permutation_index=0,
                assignments=(
                    CatTraitDieAssignment("d4", "color"),
                    CatTraitDieAssignment("d6", "color"),
                ),
            )

    def test_unknown_assignment_returns_none(self):
        result = CatTraitDiceMappingResult(
            cat_d20_value=1,
            permutation_index=0,
            assignments=(),
        )

        self.assertEqual(result.assignments, ())
        self.assertIsNone(result.trait_for_die("d4"))
        self.assertIsNone(result.die_for_trait("color"))

    def test_assignments_and_result_are_frozen(self):
        assignment = CatTraitDieAssignment(
            die="d4",
            trait="color",
        )

        result = CatTraitDiceMappingResult(
            cat_d20_value=1,
            permutation_index=0,
            assignments=(assignment,),
        )

        with self.assertRaises(FrozenInstanceError):
            assignment.trait = "sex"

        with self.assertRaises(FrozenInstanceError):
            result.assignments = ()

        with self.assertRaises(TypeError):
            _ = assignment["trait"]

        with self.assertRaises(TypeError):
            _ = result["assignments"]


if __name__ == "__main__":
    unittest.main()
