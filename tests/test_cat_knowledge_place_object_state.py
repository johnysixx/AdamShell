from core.entity.components import SpatialVector3
import unittest

from cats.cat_knowledge import CatKnowledge
from cats.cat_knowledge_objects import (
    CatKnownPlace,
    CatKnownPlaceDetails,
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

    def test_known_place_details_are_object_only(
        self
    ):
        details = (
            CatKnownPlaceDetails(
                pair_id="pair_1",
                exploration_stage=2,
            )
        )

        place = (
            CatKnowledge.remember_place(
                cat=self.cat,
                layer="quantum_layer",
                position=SpatialVector3(
                    x=1.0,
                    y=2.0,
                    z=3.0,
                ),
                details=details,
            )
        )

        self.assertIsInstance(
            place.details,
            CatKnownPlaceDetails,
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
                    place.details,
                    name,
                )
            )

        self.assertEqual(
            place.details.pair_id,
            "pair_1",
        )

        self.assertEqual(
            place.details.exploration_stage,
            2,
        )

    def test_repeated_place_details_merge_as_objects(
        self
    ):
        position = SpatialVector3(
            x=4.0,
            y=5.0,
            z=6.0,
        )

        CatKnowledge.remember_place(
            cat=self.cat,
            layer="quantum_layer",
            position=position,
            details=(
                CatKnownPlaceDetails(
                    pair_id="pair_1",
                )
            ),
        )

        place = (
            CatKnowledge.remember_place(
                cat=self.cat,
                layer="quantum_layer",
                position=position,
                details=(
                    CatKnownPlaceDetails(
                        exploration_stage=3,
                    )
                ),
            )
        )

        self.assertEqual(
            place.details.pair_id,
            "pair_1",
        )

        self.assertEqual(
            place.details.exploration_stage,
            3,
        )

    def test_mapping_place_details_are_rejected(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            CatKnowledge.remember_place(
                cat=self.cat,
                layer="quantum_layer",
                position=SpatialVector3.zero(),
                details={
                    "pair_id":
                        "legacy_pair",
                },
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
