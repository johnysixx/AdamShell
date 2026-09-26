import unittest
from types import SimpleNamespace

from cats.cat_birth_objects import (
    CatKittenBirthDeniedResult,
)

from cats.kitten_birth_resolver import (
    KittenBirthResolver,
)


class AllowPhysicalWorld:

    def require_physical_world(
        self,
        operation,
        cat,
    ):
        return {
            "allowed": True,
        }


class CatBirthDeniedObjectStateTests(
    unittest.TestCase
):

    def _result(self):
        return (
            CatKittenBirthDeniedResult(
                mother="mother",
                pregnancy_day=10,
                gestation_days=63,
            )
        )

    def test_denied_result_has_no_mapping_api(
        self
    ):
        result = self._result()

        self.assertEqual(
            result.mother,
            "mother",
        )

        self.assertEqual(
            result.pregnancy_day,
            10,
        )

        self.assertEqual(
            result.gestation_days,
            63,
        )

        self.assertFalse(
            result.born
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
                "reason"
            ]

    def test_boundary_preserves_existing_shape(
        self
    ):
        result = self._result()

        self.assertEqual(
            result.to_dict(),
            {
                "name": (
                    "kitten_birth_denied"
                ),
                "reason": (
                    "gestation_not_complete"
                ),
                "mother": "mother",
                "pregnancy_day": 10,
                "gestation_days": 63,
                "born": False,
            },
        )

    def test_completed_gestation_cannot_be_denied(
        self
    ):
        with self.assertRaises(
            ValueError
        ):
            CatKittenBirthDeniedResult(
                mother="mother",
                pregnancy_day=63,
                gestation_days=63,
            )

    def test_resolver_returns_boundary_without_history_event(
        self
    ):
        resolver = object.__new__(
            KittenBirthResolver
        )

        resolver.biology_gate = (
            AllowPhysicalWorld()
        )

        resolver.history = []

        mother = SimpleNamespace(
            name="mother",
            sex="female",
            reproduction=(
                SimpleNamespace(
                    pregnant=True,
                    pregnancy_day=10,
                    gestation_days=63,
                )
            ),
        )

        result = resolver.give_birth(
            mother
        )

        self.assertEqual(
            result,
            {
                "name": (
                    "kitten_birth_denied"
                ),
                "reason": (
                    "gestation_not_complete"
                ),
                "mother": "mother",
                "pregnancy_day": 10,
                "gestation_days": 63,
                "born": False,
            },
        )

        self.assertEqual(
            resolver.history,
            [],
        )


if __name__ == "__main__":
    unittest.main()
