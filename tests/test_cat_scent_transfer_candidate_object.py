import unittest

from cats.cat_perception_state import (
    CatScentTransferCandidate,
)


class CatScentTransferCandidateObjectTests(
    unittest.TestCase
):

    def test_candidate_has_no_mapping_api(
        self
    ):
        candidate = CatScentTransferCandidate(
            box_id='source',
            counterpart_box_id='target',
            identity='cat:pazuzu',
            similarity=0.95,
            source_layer='meeting_place',
            target_layer='quantum_layer',
            box_position={
                'x': 0.0,
                'y': 0.0,
                'z': 0.0,
            },
            counterpart_position={
                'x': 1.0,
                'y': 0.0,
                'z': 0.0,
            },
        )

        self.assertFalse(
            hasattr(
                candidate,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                candidate,
                '__getitem__',
            )
        )

        self.assertEqual(
            candidate.identity,
            'cat:pazuzu',
        )

        self.assertAlmostEqual(
            candidate.similarity,
            0.95,
        )


if __name__ == '__main__':
    unittest.main()
