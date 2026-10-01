import unittest

from core.entity.quantum_box import (
    QuantumBox,
)
from core.entity.quantum_box_cat_observation import (
    QuantumBoxCatObservation,
)
from core.entity.quantum_box_occupancy_state import (
    QuantumBoxOccupancyState,
)


class QuantumBoxCatObservationObjectStateTests(
    unittest.TestCase
):

    def test_unoccupied_box_returns_object(self):
        box = QuantumBox()

        observation = (
            box.cat_observation_state(
                {"type": "cat"}
            )
        )

        self.assertIsInstance(
            observation,
            QuantumBoxCatObservation,
        )

        self.assertTrue(
            observation.visible
        )

        self.assertFalse(
            observation.occupied
        )

        self.assertIs(
            observation.occupancy_state,
            QuantumBoxOccupancyState.UNOCCUPIED,
        )

    def test_observation_has_no_mapping_api(self):
        observation = QuantumBoxCatObservation(
            visible=True,
            recognized_as_quantum_box=True,
            occupied=False,
            occupancy_state=(
                QuantumBoxOccupancyState
                .UNOCCUPIED
            ),
        )

        for name in (
            "get",
            "keys",
            "items",
            "values",
            "__getitem__",
            "to_dict",
        ):
            self.assertFalse(
                hasattr(
                    observation,
                    name,
                ),
                name,
            )

        with self.assertRaises(TypeError):
            _ = observation[
                "visible"
            ]

    def test_string_occupancy_state_is_rejected(self):
        with self.assertRaises(TypeError):
            QuantumBoxCatObservation(
                visible=True,
                recognized_as_quantum_box=True,
                occupied=False,
                occupancy_state="unoccupied",
            )

    def test_hidden_observation_exposes_no_occupancy(self):
        box = QuantumBox()

        box.cat_transfer.active = True
        box.cat_transfer.state = (
            box.cat_transfer.state
            .__class__.SUPERPOSITION
        )

        observation = (
            box.cat_observation_state(
                {"type": "human"}
            )
        )

        self.assertIsInstance(
            observation,
            QuantumBoxCatObservation,
        )

        self.assertFalse(
            observation.visible
        )

        self.assertIsNone(
            observation.occupied
        )

        self.assertIsNone(
            observation.occupancy_state
        )

    def test_hidden_observation_rejects_occupancy(self):
        with self.assertRaises(ValueError):
            QuantumBoxCatObservation(
                visible=False,
                recognized_as_quantum_box=False,
                occupied=False,
                occupancy_state=None,
            )

    def test_hidden_observation_rejects_state(self):
        with self.assertRaises(ValueError):
            QuantumBoxCatObservation(
                visible=False,
                recognized_as_quantum_box=False,
                occupied=None,
                occupancy_state=(
                    QuantumBoxOccupancyState
                    .UNOCCUPIED
                ),
            )

    def test_visible_observation_requires_occupancy(self):
        with self.assertRaises(ValueError):
            QuantumBoxCatObservation(
                visible=True,
                recognized_as_quantum_box=True,
                occupied=None,
                occupancy_state=(
                    QuantumBoxOccupancyState
                    .UNOCCUPIED
                ),
            )

    def test_visible_observation_requires_state(self):
        with self.assertRaises(ValueError):
            QuantumBoxCatObservation(
                visible=True,
                recognized_as_quantum_box=True,
                occupied=False,
                occupancy_state=None,
            )

    def test_occupied_state_requires_matching_enum(self):
        with self.assertRaises(ValueError):
            QuantumBoxCatObservation(
                visible=True,
                recognized_as_quantum_box=True,
                occupied=True,
                occupancy_state=(
                    QuantumBoxOccupancyState
                    .UNOCCUPIED
                ),
            )

    def test_unoccupied_state_requires_matching_enum(self):
        with self.assertRaises(ValueError):
            QuantumBoxCatObservation(
                visible=True,
                recognized_as_quantum_box=True,
                occupied=False,
                occupancy_state=(
                    QuantumBoxOccupancyState
                    .CAT_TRANSFER_OCCUPIED
                ),
            )

    def test_occupancy_domain_is_finite(self):
        self.assertEqual(
            {
                state.value
                for state
                in QuantumBoxOccupancyState
            },
            {
                "unoccupied",
                "cat_transfer_occupied",
            },
        )


if __name__ == "__main__":
    unittest.main()
