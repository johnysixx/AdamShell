from core.entity.components import SpatialVector3
import unittest
from dataclasses import FrozenInstanceError, replace
from universe.aroma_composition import AromaComposition

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

        self.cat.position = SpatialVector3(x=0.0, y=0.0, z=0.0)

        ambient = (
            self.meeting_place
            .ambient_aroma
        )

        ambient.profile = (
            AromaComposition.from_pairs(
                ("berry", 1.0),
                ("ethanol", 0.5),
            )
        )

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

        self.assertIsInstance(
            ambient.components,
            AromaComposition,
        )

        self.assertEqual(
            ambient.components.amount(
                "berry"
            ),
            1.0,
        )

        self.assertEqual(
            ambient.components.amount(
                "ethanol"
            ),
            0.5,
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



    def test_ambient_record_is_immutable(self):
        ambient = self.ambient()

        with self.assertRaises(FrozenInstanceError):
            ambient.source = "other"

        with self.assertRaises(FrozenInstanceError):
            ambient.components = AromaComposition.empty()

        with self.assertRaises(FrozenInstanceError):
            ambient.recognition = CatAromaRecognition()

        with self.assertRaises(FrozenInstanceError):
            ambient.recognition.recognized = True

        with self.assertRaises(FrozenInstanceError):
            ambient.components.entries[0].intensity = 9.0

    def test_ambient_replacement_preserves_original(self):
        original = self.ambient()

        updated = replace(
            original,
            source="new_source",
        )

        self.assertIsNot(updated, original)
        self.assertEqual(original.source, "raspberry_rum")
        self.assertEqual(updated.source, "new_source")

        self.assertIs(
            updated.components,
            original.components,
        )

        self.assertIs(
            updated.recognition,
            original.recognition,
        )

    def test_ambient_requires_canonical_objects(self):
        composition = AromaComposition.from_pairs(
            ("berry", 1.0),
        )

        with self.assertRaises(TypeError):
            CatAmbientAroma(
                source="invalid",
                components={"berry": 1.0},
                recognition=CatAromaRecognition(),
            )

        with self.assertRaises(TypeError):
            CatAmbientAroma(
                source="invalid",
                components=composition,
                recognition={"recognized": False},
            )

    def test_sniff_preserves_previous_ambient_snapshot(self):
        first = self.ambient()

        self.meeting_place.ambient_aroma.profile = (
            AromaComposition.from_pairs(
                ("ozone", 0.9),
            )
        )

        second = self.ambient()

        self.assertIsNot(first, second)

        self.assertEqual(
            first.components.amount("berry"),
            1.0,
        )

        self.assertEqual(
            first.components.amount("ozone"),
            0.0,
        )

        self.assertEqual(
            second.components.amount("ozone"),
            0.9,
        )

        self.assertEqual(
            second.components.amount("berry"),
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
