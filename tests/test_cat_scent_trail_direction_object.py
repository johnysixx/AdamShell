from core.entity.components import SpatialVector3
import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_intention_state import (
    CatScentSearchTarget,
)
from cats.cat_knowledge import CatKnowledge
from cats.cat_scent_direction_state import (
    CatScentTrailDirection,
)


class CatScentTrailDirectionObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name='tracker',
            color='black',
            fur_length='short',
        )

    def test_direction_has_no_mapping_api(
        self
    ):
        direction = CatScentTrailDirection(
            inferred=True,
            confidence=0.8,
        )

        self.assertFalse(
            hasattr(
                direction,
                'get',
            )
        )

        self.assertFalse(
            hasattr(
                direction,
                '__getitem__',
            )
        )

        self.assertTrue(
            direction.inferred
        )

    def test_failed_inference_is_object(
        self
    ):
        result = (
            CatKnowledge
            .infer_scent_direction(
                cat=self.cat,
                identity='cat:pazuzu',
                layer='quantum_layer',
            )
        )

        self.assertIsInstance(
            result,
            CatScentTrailDirection,
        )

        self.assertFalse(
            result.inferred
        )

        self.assertEqual(
            result.reason,
            'not_enough_scent_points',
        )

    def test_successful_inference_is_object(
        self
    ):
        CatKnowledge.remember_scent_place(
            cat=self.cat,
            layer='quantum_layer',
            position=SpatialVector3(x=1.0, y=0.0, z=0.0),
            source_id='trace_a',
            recognized_identity=(
                'cat:pazuzu'
            ),
            components={},
            perceived_intensity=0.4,
            universe_tick=10,
        )

        CatKnowledge.remember_scent_place(
            cat=self.cat,
            layer='quantum_layer',
            position=SpatialVector3(x=4.0, y=0.0, z=0.0),
            source_id='trace_b',
            recognized_identity=(
                'cat:pazuzu'
            ),
            components={},
            perceived_intensity=0.6,
            universe_tick=20,
        )

        self.cat.knowledge.scent_clock_tick = 20

        result = (
            CatKnowledge
            .infer_scent_direction(
                cat=self.cat,
                identity='cat:pazuzu',
                layer='quantum_layer',
            )
        )

        self.assertIsInstance(
            result,
            CatScentTrailDirection,
        )

        self.assertTrue(
            result.inferred
        )

        self.assertEqual(
            result.to_source_id,
            'trace_b',
        )

        self.assertEqual(
            result.unit_vector,
            SpatialVector3(x=1.0, y=0.0, z=0.0),
        )

    def test_owner_rejects_mapping_direction(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            CatScentSearchTarget(
                identity='cat:pazuzu',
                trail_direction={
                    'inferred': True,
                },
            )


if __name__ == '__main__':
    unittest.main()
