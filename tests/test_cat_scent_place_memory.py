import unittest

from universe.universe import Universe
from cats.cats import Cats
from cats.cat_olfaction import CatOlfaction
from cats.cat_knowledge import CatKnowledge
from universe.aroma_residue import AromaResidue


class CatScentPlaceMemoryTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.pazuzu = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short"
        )

        self.observer = self.cats.create_cat(
            name="observer",
            color="gray",
            fur_length="short"
        )

        self.pazuzu["position"] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        self.observer["position"] = {
            "x": 0.0,
            "y": 0.0,
            "z": 0.0
        }

        self.observer[
            "current_layer"
        ] = "quantum_layer"

        self.cats.learn_cat_aroma(
            observer=self.observer,
            observed_cat=self.pazuzu
        )

        self.box = (
            self.universe
            .create_quantum_box()
        )

        self.box.position = {
            "x": 2.0,
            "y": 0.0,
            "z": 0.0
        }

        AromaResidue.transfer(
            source_profile=(
                self.pazuzu[
                    "aroma"
                ]
            ),
            target=self.box,
            source_identity="pazuzu",
            fraction=0.30
        )

    def sniff_and_remember(self):
        olfaction = CatOlfaction.sniff(
            self.observer,
            self.universe
        )

        return (
            CatKnowledge
            .remember_olfaction(
                cat=self.observer,
                olfaction=olfaction,
                current_layer=(
                    "quantum_layer"
                ),
                universe_tick=10
            )
        )

    def test_cat_remembers_where_pazuzu_was_smelt(
        self
    ):
        self.sniff_and_remember()

        memories = (
            self.observer[
                "knowledge"
            ][
                "known_scent_places"
            ]
        )

        pazuzu_memories = [
            memory
            for memory in memories
            if memory[
                "identity"
            ] == "cat:pazuzu"
        ]

        self.assertEqual(
            len(pazuzu_memories),
            1
        )

        memory = pazuzu_memories[0]

        self.assertEqual(
            memory["source_id"],
            self.box.id
        )

        self.assertEqual(
            memory["position"],
            self.box.position
        )

    def test_repeated_smell_increases_confidence(
        self
    ):
        self.sniff_and_remember()

        first = (
            self.observer[
                "knowledge"
            ][
                "known_scent_places"
            ][0]
        )["confidence"]

        self.sniff_and_remember()

        second = (
            self.observer[
                "knowledge"
            ][
                "known_scent_places"
            ][0]
        )["confidence"]

        self.assertGreater(
            second,
            first
        )

    def test_memory_survives_after_residue_fades(
        self
    ):
        self.sniff_and_remember()

        AromaResidue.decay(
            self.box,
            ticks=1000
        )

        memory = next(
            item
            for item
            in self.observer[
                "knowledge"
            ][
                "known_scent_places"
            ]
            if item[
                "identity"
            ] == "cat:pazuzu"
        )

        self.assertEqual(
            memory["source_id"],
            self.box.id
        )


if __name__ == "__main__":
    unittest.main()