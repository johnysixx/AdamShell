import unittest

from universe.physics_layers import (
    UniversePhysicsLayers
)
from universe.universe import Universe


class UniversePhysicsLayersObjectStateTests(
    unittest.TestCase
):

    def _assert_object_only(self, value):
        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
        ):
            self.assertFalse(
                hasattr(
                    value,
                    mapping_method,
                )
            )

        with self.assertRaises(TypeError):
            _ = value["quantum"]

    def test_physics_layers_are_object_only(
        self
    ):
        layers = Universe().physics_layers

        self.assertIsInstance(
            layers,
            UniversePhysicsLayers,
        )
        self._assert_object_only(layers)

    def test_initial_layers_are_preserved(
        self
    ):
        layers = Universe().physics_layers

        self.assertTrue(layers.classical)
        self.assertFalse(layers.quantum)

    def test_enabling_quantum_keeps_same_object(
        self
    ):
        universe = Universe()
        layers = universe.physics_layers

        universe.enable_quantum_layer()

        self.assertIs(
            universe.physics_layers,
            layers,
        )
        self.assertTrue(layers.classical)
        self.assertTrue(layers.quantum)
        self.assertTrue(
            universe.quantum_state.enabled
        )

    def test_repeated_enable_is_idempotent(
        self
    ):
        layers = UniversePhysicsLayers()

        layers.enable_quantum()
        layers.enable_quantum()

        self.assertTrue(layers.classical)
        self.assertTrue(layers.quantum)

    def test_to_dict_returns_detached_boundary(
        self
    ):
        layers = UniversePhysicsLayers()
        layers.enable_quantum()

        snapshot = layers.to_dict()

        self.assertIsInstance(snapshot, dict)
        snapshot["classical"] = False
        snapshot["quantum"] = False

        self.assertTrue(layers.classical)
        self.assertTrue(layers.quantum)


if __name__ == "__main__":
    unittest.main()
