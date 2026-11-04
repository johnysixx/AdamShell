import unittest

from meeting_place.bar_objects import (
    DrinkRecipe,
)
from meeting_place.how_to_mix_drinks import (
    HowToMixDrinks,
)
from meeting_place.drink_recipe_status import (
    DrinkRecipeStatus,
)


class DrinkRecipeStatusObjectStateTests(
    unittest.TestCase
):

    def _recipe(
        self,
        initial_status=None
    ):
        return DrinkRecipe(
            name="singularity",
            origin="test_recipe",
            ingredients=[],
            initial_status=initial_status,
        )

    def test_regular_recipe_has_no_testing_status(self):
        recipe = self._recipe()

        self.assertIsNone(
            recipe.status
        )

        self.assertNotIn(
            "status",
            recipe.to_dict(),
        )

    def test_testing_status_is_enum(self):
        recipe = self._recipe(
            DrinkRecipeStatus.TESTING
        )

        self.assertIs(
            recipe.status,
            DrinkRecipeStatus.TESTING,
        )

        self.assertEqual(
            recipe.to_dict()["status"],
            "testing",
        )

    def test_string_status_assignment_is_rejected(self):
        recipe = self._recipe()

        with self.assertRaises(TypeError):
            recipe.status = "testing"

    def test_string_initial_status_is_rejected(self):
        with self.assertRaises(TypeError):
            self._recipe(
                "testing"
            )

    def test_approval_transition_uses_enum(self):
        recipe = self._recipe(
            DrinkRecipeStatus.TESTING
        )

        for index in range(5):
            recipe.record_tasting(
                guest=f"guest_{index}",
                liked=index < 4,
            )

        self.assertIs(
            recipe.status,
            DrinkRecipeStatus.APPROVED,
        )

        self.assertTrue(
            recipe.approved
        )

        self.assertEqual(
            recipe.to_dict()["status"],
            "approved",
        )

    def test_rejection_transition_uses_enum(self):
        recipe = self._recipe(
            DrinkRecipeStatus.TESTING
        )

        for index in range(5):
            recipe.record_tasting(
                guest=f"guest_{index}",
                liked=index < 3,
            )

        self.assertIs(
            recipe.status,
            DrinkRecipeStatus.REJECTED,
        )

        self.assertFalse(
            recipe.approved
        )

        self.assertEqual(
            recipe.to_dict()["status"],
            "rejected",
        )

    def test_nested_recipe_effects_snapshot_is_detached(self):
        recipe = self._recipe()

        effects = {
            "quantum_glow": {
                "intensity": [1, 2],
                "metadata": {
                    "sources": ["original"],
                },
            },
        }

        recipe.effects = effects

        first = recipe.to_dict()
        second = recipe.to_dict()

        first["effects"]["quantum_glow"][
            "intensity"
        ].append(99)

        first["effects"]["quantum_glow"][
            "metadata"
        ]["sources"].append("snapshot_only")

        self.assertEqual(
            effects["quantum_glow"]["intensity"],
            [1, 2],
        )

        self.assertEqual(
            effects["quantum_glow"][
                "metadata"
            ]["sources"],
            ["original"],
        )

        self.assertEqual(
            second["effects"]["quantum_glow"][
                "intensity"
            ],
            [1, 2],
        )

        self.assertEqual(
            second["effects"]["quantum_glow"][
                "metadata"
            ]["sources"],
            ["original"],
        )

        self.assertIs(
            recipe.effects,
            effects,
        )

        self.assertIsNot(
            first["effects"]["quantum_glow"],
            effects["quantum_glow"],
        )

    def test_recipe_effects_snapshot_ignores_live_changes(self):
        recipe = self._recipe()

        effects = {
            "resonance": {
                "notes": ["original"],
            },
        }

        recipe.effects = effects

        snapshot = recipe.to_dict()

        effects["resonance"]["notes"].append(
            "live_change"
        )

        self.assertEqual(
            snapshot["effects"][
                "resonance"
            ]["notes"],
            ["original"],
        )

        current = recipe.to_dict()

        self.assertEqual(
            current["effects"][
                "resonance"
            ]["notes"],
            ["original", "live_change"],
        )

        snapshot["effects"]["resonance"][
            "notes"
        ].append("snapshot_only")

        snapshot["effects"].clear()

        self.assertEqual(
            effects["resonance"]["notes"],
            ["original", "live_change"],
        )

        self.assertIs(
            recipe.effects,
            effects,
        )

        self.assertEqual(
            recipe.to_dict()["effects"][
                "resonance"
            ]["notes"],
            ["original", "live_change"],
        )

    def test_recipe_book_keeps_live_recipe_and_detached_effects(self):
        book = HowToMixDrinks()

        recipe = book.add_created_recipe(
            name="singularity",
            ingredients=["lemonade"],
        )

        effects = {
            "space_time": {
                "observations": ["original"],
            },
        }

        recipe.effects = effects

        tasting = recipe.record_tasting(
            guest="newton",
            liked=True,
        )

        first = recipe.to_dict()
        second = recipe.to_dict()

        self.assertIs(
            book.recipes["singularity"],
            recipe,
        )

        self.assertIs(
            recipe.effects,
            effects,
        )

        self.assertIs(
            recipe.tastings[0],
            tasting,
        )

        self.assertIs(
            recipe.status,
            DrinkRecipeStatus.TESTING,
        )

        first["effects"]["space_time"][
            "observations"
        ].append("snapshot_only")

        self.assertEqual(
            effects["space_time"]["observations"],
            ["original"],
        )

        self.assertEqual(
            second["effects"]["space_time"][
                "observations"
            ],
            ["original"],
        )

        effects["space_time"]["observations"].append(
            "live_change"
        )

        self.assertEqual(
            second["effects"]["space_time"][
                "observations"
            ],
            ["original"],
        )

        self.assertEqual(
            recipe.to_dict()["effects"][
                "space_time"
            ]["observations"],
            ["original", "live_change"],
        )

        self.assertEqual(
            recipe.to_dict()["tastings"][0]["guest"],
            "newton",
        )

        self.assertIs(
            book.recipes["singularity"],
            recipe,
        )

        self.assertIs(
            recipe.tastings[0],
            tasting,
        )

    def test_status_domain_is_finite(self):
        self.assertEqual(
            {
                status.value
                for status
                in DrinkRecipeStatus
            },
            {
                "testing",
                "approved",
                "rejected",
            },
        )


if __name__ == "__main__":
    unittest.main()
