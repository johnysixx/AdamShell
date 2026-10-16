import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from meeting_place.cat_d20_profile_preparation_state import (
    CatD20ProfilePreparationFailedResult,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class CatD20ProfilePreparationObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.bar = MeetingPlace(
            self.universe
        )

    def assert_failure(
        self,
        result,
        reason,
    ):
        self.assertIsInstance(
            result,
            CatD20ProfilePreparationFailedResult,
        )

        self.assertEqual(
            result.name,
            "cat_d20_pazuzu_profile_failed",
        )

        self.assertEqual(
            result.reason,
            reason,
        )

        self.assertFalse(
            result.prepared
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
            "__getitem__",
            "__setitem__",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                ),
                mapping_method,
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "reason"
            ]

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.reason = "changed"

    def test_missing_cats_layer_is_object(
        self,
    ):
        self.universe.cats_layer = None

        result = (
            self.bar
            .cat_d20_prepare_pazuzu_profile()
        )

        self.assert_failure(
            result,
            "cats_layer_missing",
        )

    def test_missing_cat_d20_is_object(
        self,
    ):
        self.universe.cats_layer = (
            SimpleNamespace(
                cats=[],
            )
        )

        result = (
            self.bar
            .cat_d20_prepare_pazuzu_profile()
        )

        self.assert_failure(
            result,
            "cat_d20_missing",
        )


if __name__ == "__main__":
    unittest.main()
