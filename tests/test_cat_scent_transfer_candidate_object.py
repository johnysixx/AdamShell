from core.entity.components import SpatialVector3
import unittest
from dataclasses import FrozenInstanceError, replace

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
            box_position=SpatialVector3(x=0.0, y=0.0, z=0.0),
            counterpart_position=SpatialVector3(x=1.0, y=0.0, z=0.0),
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



    @staticmethod
    def sample_candidate():
        return CatScentTransferCandidate(
            box_id="source",
            counterpart_box_id="target",
            identity="cat:pazuzu",
            similarity=0.95,
            source_layer="meeting_place",
            target_layer="quantum_layer",
            box_position=SpatialVector3(
                x=0.0, y=0.0, z=0.0
            ),
            counterpart_position=SpatialVector3(
                x=1.0, y=0.0, z=0.0
            ),
        )

    def test_candidate_is_frozen(self):
        candidate = self.sample_candidate()

        changes = (
            ("box_id", "other"),
            ("counterpart_box_id", "other"),
            ("identity", "other"),
            ("similarity", 0.1),
            ("source_layer", "other"),
            ("target_layer", "other"),
            ("box_position", None),
            ("counterpart_position", None),
        )

        for name, value in changes:
            with self.subTest(field=name):
                with self.assertRaises(FrozenInstanceError):
                    setattr(candidate, name, value)

    def test_candidate_positions_are_immutable(self):
        candidate = self.sample_candidate()

        self.assertIsInstance(
            candidate.box_position,
            SpatialVector3,
        )

        self.assertIsInstance(
            candidate.counterpart_position,
            SpatialVector3,
        )

        with self.assertRaises(FrozenInstanceError):
            candidate.box_position.x = 9.0

        with self.assertRaises(FrozenInstanceError):
            candidate.counterpart_position.y = 9.0

        self.assertEqual(
            candidate.box_position.x,
            0.0,
        )

        self.assertEqual(
            candidate.counterpart_position.x,
            1.0,
        )

    def test_candidate_replacement_preserves_original(self):
        original = self.sample_candidate()

        updated = replace(
            original,
            similarity=0.75,
            counterpart_box_id="new_target",
        )

        self.assertIsNot(updated, original)

        self.assertEqual(original.similarity, 0.95)
        self.assertEqual(updated.similarity, 0.75)

        self.assertEqual(
            original.counterpart_box_id,
            "target",
        )

        self.assertEqual(
            updated.counterpart_box_id,
            "new_target",
        )

        self.assertIs(
            original.box_position,
            updated.box_position,
        )

        self.assertIs(
            original.counterpart_position,
            updated.counterpart_position,
        )

    def test_candidate_rejects_mapping_positions(self):
        with self.assertRaises(TypeError):
            CatScentTransferCandidate(
                box_position={
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0,
                },
            )

        with self.assertRaises(TypeError):
            CatScentTransferCandidate(
                counterpart_position={
                    "x": 1.0,
                    "y": 0.0,
                    "z": 0.0,
                },
            )

        empty = CatScentTransferCandidate()

        self.assertIsNone(empty.box_position)
        self.assertIsNone(empty.counterpart_position)


if __name__ == '__main__':
    unittest.main()
