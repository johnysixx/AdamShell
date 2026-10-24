import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from meeting_place.cat_d20_turn_state import (
    CatD20TurnFailedResult,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class CatD20TurnResultObjectStateTests(
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
        cat=None,
    ):
        self.assertIsInstance(
            result,
            CatD20TurnFailedResult,
        )

        self.assertEqual(
            result.name,
            "cat_d20_turn_failed",
        )

        self.assertEqual(
            result.reason,
            reason,
        )

        self.assertEqual(
            result.cat,
            cat,
        )

        self.assertFalse(
            result.turned
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "setdefault",
            "__getitem__",
            "__setitem__",
            "to_dict",
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
            result.reason = (
                "changed"
            )

    def test_missing_cats_layer_is_object(
        self,
    ):
        self.universe.cats_layer = None

        result = (
            self.bar
            .turn_cat_d20_in_box()
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
            .turn_cat_d20_in_box()
        )

        self.assert_failure(
            result,
            "cat_d20_missing",
        )

    def test_missing_cat_d20_box_is_object(
        self,
    ):
        cat = SimpleNamespace(
            name="cat_d20",
            special_traits=[
                "d20_cat",
            ],
        )

        self.universe.cats_layer = (
            SimpleNamespace(
                cats=[
                    cat,
                ],
            )
        )

        self.bar.cat_d20_box = None

        result = (
            self.bar
            .turn_cat_d20_in_box()
        )

        self.assert_failure(
            result,
            "cat_d20_box_missing",
            cat="cat_d20",
        )

    def test_cat_not_in_box_is_object(
        self,
    ):
        cat = SimpleNamespace(
            name="cat_d20",
            special_traits=[
                "d20_cat",
            ],
        )

        self.universe.cats_layer = (
            SimpleNamespace(
                cats=[
                    cat,
                ],
            )
        )

        self.bar.cat_d20_box = (
            SimpleNamespace(
                occupied_by=(
                    "someone_else"
                ),
            )
        )

        result = (
            self.bar
            .turn_cat_d20_in_box()
        )

        self.assert_failure(
            result,
            "cat_d20_not_in_box",
            cat="cat_d20",
        )


if __name__ == "__main__":
    unittest.main()
