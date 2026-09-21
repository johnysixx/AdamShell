import unittest

from cats.cat_trait_dice_mapping import (
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
            set(result.die_to_trait),
            set(CatTraitDiceMapping.DICE),
        )

    def test_inverse_trait_mapping_is_available_through_methods(self):
        result = CatTraitDiceMapping().resolve(3)

        for die_name, trait in result.die_to_trait.items():
            self.assertEqual(
                result.trait_for_die(die_name),
                trait,
            )
            self.assertEqual(
                result.die_for_trait(trait),
                die_name,
            )

    def test_result_has_no_mapping_compatibility(self):
        result = CatTraitDiceMapping().resolve(1)

        with self.assertRaises(TypeError):
            _ = result["die_to_trait"]

        with self.assertRaises(AttributeError):
            result.get("die_to_trait")

    def test_to_dict_returns_detached_snapshot(self):
        result = CatTraitDiceMapping().resolve(1)
        snapshot = result.to_dict()

        first_die = next(iter(snapshot["die_to_trait"]))
        snapshot["die_to_trait"][first_die] = "changed"

        self.assertNotEqual(
            result.die_to_trait[first_die],
            "changed",
        )

    def test_constructor_detaches_input_registries(self):
        die_to_trait = {"d4": "color"}
        trait_to_die = {"color": "d4"}

        result = CatTraitDiceMappingResult(
            cat_d20_value=1,
            permutation_index=0,
            die_to_trait=die_to_trait,
            trait_to_die=trait_to_die,
        )

        die_to_trait["d4"] = "sex"
        trait_to_die["color"] = "d6"

        self.assertEqual(
            result.die_to_trait["d4"],
            "color",
        )
        self.assertEqual(
            result.trait_to_die["color"],
            "d4",
        )


if __name__ == "__main__":
    unittest.main()
