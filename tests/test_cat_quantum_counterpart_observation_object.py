from core.entity.components import SpatialVector3
import unittest

from cats.cat_quantum_observation_state import (
    CatQuantumCounterpartObservation,
)


class CatQuantumCounterpartObservationObjectTests(
    unittest.TestCase
):

    def test_observation_has_no_mapping_api(
        self
    ):
        observation = (
            CatQuantumCounterpartObservation(
                source_box_id='source',
                counterpart_box_id='target',
                source_layer='quantum_layer',
                counterpart_layer='meeting_place',
                temporary=True,
                pair_currently_valid=True,
            )
        )

        self.assertFalse(
            hasattr(
                observation,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                observation,
                '__getitem__',
            )
        )

        self.assertEqual(
            observation.counterpart_box_id,
            'target',
        )

    def test_event_serialization_is_explicit(
        self
    ):
        observation = (
            CatQuantumCounterpartObservation(
                source_box_id='source',
                counterpart_box_id='target',
                counterpart_position=SpatialVector3(x=1.0, y=2.0, z=0.0),
                pair_currently_valid=True,
            )
        )

        payload = observation.to_dict()

        self.assertIsInstance(
            payload,
            dict,
        )

        self.assertEqual(
            payload['source_box_id'],
            'source',
        )

        self.assertTrue(
            payload['pair_currently_valid']
        )

        self.assertFalse(
            hasattr(
                observation,
                '__getitem__',
            )
        )


if __name__ == '__main__':
    unittest.main()
