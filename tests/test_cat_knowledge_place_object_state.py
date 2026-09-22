from core.entity.components import SpatialVector3
import unittest

from cats.cat_knowledge import CatKnowledge
from cats.cat_knowledge_objects import (
    CatKnownPlace,
    CatScentPlaceMemory,
)
from cats.cats import Cats
from universe.universe import Universe


class CatKnowledgePlaceObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.cats = Cats(
            self.universe
        )

        self.cat = (
            self.cats.create_cat(
                name='tracker',
                color='black',
                fur_length='short',
            )
        )

    def test_known_place_is_object_state(
        self
    ):
        place = (
            CatKnowledge.remember_place(
                cat=self.cat,
                layer='quantum_layer',
                position=SpatialVector3(x=1.0, y=2.0, z=3.0),
            )
        )

        self.assertIsInstance(
            place,
            CatKnownPlace,
        )

        self.assertIsInstance(
            self.cat.knowledge.known_places[0],
            CatKnownPlace,
        )

    def test_scent_place_is_object_state(
        self
    ):
        memory = (
            CatKnowledge
            .remember_scent_place(
                cat=self.cat,
                layer='quantum_layer',
                position=SpatialVector3(x=4.0, y=0.0, z=0.0),
                source_id='trace',
                recognized_identity=(
                    'cat:pazuzu'
                ),
                perceived_intensity=0.7,
                universe_tick=10,
            )
        )

        self.assertIsInstance(
            memory,
            CatScentPlaceMemory,
        )

        self.assertIsInstance(
            self.cat.knowledge.known_scent_places[0],
            CatScentPlaceMemory,
        )


if __name__ == '__main__':
    unittest.main()
