import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from cats.cats import Cats
from cats.cat_knowledge import CatKnowledge
from cats.cat_olfaction import CatOlfaction
from cats.cat_olfaction_state import (
    CatAmbientAroma,
    CatAromaRecognition,
)


class CatAmbientAromaObjectTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.meeting_place = MeetingPlace(
            self.universe
        )

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="ambient_cat",
            color="black",
            fur_length="short",
        )

        self.cat.current_layer = (
            "meeting_place"
        )

        self.cat.position = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0,
        }

        ambient = (
            self.meeting_place
            .ambient_aroma
        )

        ambient.profile = {
            "berry": 1.0,
            "ethanol": 0.5,
        }

        ambient.dominant_source = (
            "raspberry_rum"
        )

    def ambient(self):
        result = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        return result.ambient_aroma

    def test_ambient_aroma_is_object(
        self
    ):
        ambient = self.ambient()

        self.assertIsInstance(
            ambient,
            CatAmbientAroma,
        )

        self.assertFalse(
            hasattr(
                ambient,
                "get",
            )
        )

        self.assertFalse(
            hasattr(
                ambient,
                "__getitem__",
            )
        )

    def test_ambient_aroma_has_object_recognition(
        self
    ):
        ambient = self.ambient()

        self.assertEqual(
            ambient.source,
            "raspberry_rum",
        )

        self.assertEqual(
            ambient.components,
            {
                "berry": 1.0,
                "ethanol": 0.5,
            },
        )

        self.assertIsInstance(
            ambient.recognition,
            CatAromaRecognition,
        )

    def test_ambient_aroma_can_be_remembered(
        self
    ):
        olfaction = CatOlfaction.sniff(
            self.cat,
            self.universe,
        )

        remembered = (
            CatKnowledge.remember_olfaction(
                cat=self.cat,
                olfaction=olfaction,
                current_layer=(
                    "meeting_place"
                ),
                universe_tick=10,
            )
        )

        ambient_memories = [
            memory
            for memory in remembered
            if memory.source_id
            == "ambient"
        ]

        self.assertEqual(
            len(
                ambient_memories
            ),
            1,
        )

        self.assertEqual(
            ambient_memories[
                0
            ].identity,
            "raspberry_rum",
        )


if __name__ == "__main__":
    unittest.main()
