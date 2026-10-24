import unittest

from cats.cat_exploration_memory_details import (
    CatExplorationMemoryDetails,
)
from cats.memory import CatMemory
from core.entity.components import (
    SpatialVector3,
)


class CatExplorationMemoryDetailsObjectStateTests(
    unittest.TestCase
):

    def test_details_are_object_only(
        self
    ):
        details = (
            CatExplorationMemoryDetails(
                target_layer=
                    "quantum_layer",
                position=
                    SpatialVector3.zero(),
                pair_id="pair_1",
            )
        )

        for name in (
            "get",
            "keys",
            "items",
            "values",
            "update",
            "__getitem__",
            "__setitem__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    details,
                    name,
                )
            )

        self.assertEqual(
            details.target_layer,
            "quantum_layer",
        )

    def test_mapping_position_is_rejected(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            CatExplorationMemoryDetails(
                target_layer=
                    "quantum_layer",
                position={
                    "x": 1.0,
                    "y": 2.0,
                    "z": 3.0,
                },
            )

    def test_memory_keeps_exploration_details_object(
        self
    ):
        memory = CatMemory(
            "exploration_memory_cat"
        )

        position = (
            SpatialVector3(
                x=1.0,
                y=2.0,
                z=3.0,
            )
        )

        returned = memory.remember(
            event_type=(
                "successful_exploration"
            ),
            location=position,
            details=(
                CatExplorationMemoryDetails(
                    target_layer=
                        "quantum_layer",
                    position=
                        position,
                    pair_id=
                        "pair_1",
                )
            ),
        )

        stored = (
            memory.records()[0]
        )

        self.assertIsInstance(
            returned.details,
            CatExplorationMemoryDetails,
        )

        self.assertIsInstance(
            stored.details,
            CatExplorationMemoryDetails,
        )

        self.assertIsInstance(
            stored.location,
            SpatialVector3,
        )

        self.assertIsInstance(
            stored.details.position,
            SpatialVector3,
        )

        self.assertEqual(
            stored.details.target_layer,
            "quantum_layer",
        )

        self.assertFalse(
            hasattr(
                memory,
                "public_state",
            )
        )


if __name__ == "__main__":
    unittest.main()
