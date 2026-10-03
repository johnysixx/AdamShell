import unittest

from cats.cat_door import CatDoor
from cats.cat_door_factory import (
    CatDoorFactory,
)
from cats.cat_door_pair_state import (
    CatDoorPair,
)
from cats.cat_door_registry import (
    CatDoorRegistry,
)


class CatDoorPairObjectStateTests(
    unittest.TestCase
):

    def assert_not_mapping(
        self,
        pair,
    ):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    pair,
                    mapping_method,
                )
            )

        self.assertFalse(
            hasattr(
                pair,
                "to_dict",
            )
        )

        with self.assertRaises(
            TypeError
        ):
            _ = pair[
                "forward"
            ]

    def test_factory_returns_pair_object(
        self
    ):
        pair = (
            CatDoorFactory
            .create_pair(
                name="layer_pair",
                layer_a="layer_a",
                layer_b="layer_b",
            )
        )

        self.assertIsInstance(
            pair,
            CatDoorPair,
        )

        self.assertIsInstance(
            pair.forward,
            CatDoor,
        )

        self.assertIsInstance(
            pair.backward,
            CatDoor,
        )

        self.assertEqual(
            pair.forward.source_layer,
            "layer_a",
        )

        self.assertEqual(
            pair.forward.target_layer,
            "layer_b",
        )

        self.assertEqual(
            pair.backward.source_layer,
            "layer_b",
        )

        self.assertEqual(
            pair.backward.target_layer,
            "layer_a",
        )

        self.assert_not_mapping(
            pair
        )

    def test_registry_returns_same_pair_objects_it_registers(
        self
    ):
        registry = (
            CatDoorRegistry()
        )

        pair = (
            registry.create_pair(
                name="layer_pair",
                layer_a="layer_a",
                layer_b="layer_b",
            )
        )

        self.assertIs(
            registry.find(
                source_layer="layer_a",
                target_layer="layer_b",
            ),
            pair.forward,
        )

        self.assertIs(
            registry.find(
                source_layer="layer_b",
                target_layer="layer_a",
            ),
            pair.backward,
        )

        self.assertIs(
            registry.doors[0],
            pair.forward,
        )

        self.assertIs(
            registry.doors[1],
            pair.backward,
        )

    def test_pair_requires_cat_door_objects(
        self
    ):
        door = CatDoor(
            name="valid",
            source_layer="layer_a",
            target_layer="layer_b",
        )

        with self.assertRaises(
            TypeError
        ):
            CatDoorPair(
                forward=object(),
                backward=door,
            )

        with self.assertRaises(
            TypeError
        ):
            CatDoorPair(
                forward=door,
                backward=object(),
            )


if __name__ == "__main__":
    unittest.main()
