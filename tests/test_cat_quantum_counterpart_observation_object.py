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

    def test_observation_has_no_serialization_api(
        self
    ):
        observation = (
            CatQuantumCounterpartObservation(
                source_box_id='source',
                counterpart_box_id='target',
                counterpart_position=SpatialVector3(
                    x=1.0,
                    y=2.0,
                    z=0.0,
                ),
                pair_currently_valid=True,
            )
        )

        self.assertFalse(
            hasattr(
                observation,
                'to_dict',
            )
        )

        self.assertEqual(
            observation.source_box_id,
            'source',
        )

        self.assertTrue(
            observation.pair_currently_valid
        )


if __name__ == '__main__':
    unittest.main()
