import unittest

from meeting_place.bar_objects import (
    DrinkRecipe,
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
