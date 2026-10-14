import unittest
from universe.aroma_composition import AromaComposition

from universe.universe import Universe
from multiverse import UniverseRegistry
from universe.molecules import Molecules
from universe.aroma_profile import AromaProfile
from universe.aroma_foundations import (
    AromaFoundations
)
from cats.cats import Cats
from meeting_place.meeting_place import (
    MeetingPlace
)
from core.entity.cronenberg import Cronenberg


class ChemicalAromaFoundationsTests(
    unittest.TestCase
):

    def test_raspberry_rum_has_chemical_base(
        self
    ):
        universe = Universe()

        aromas = AromaFoundations(
            universe
        )

        rum = aromas.get_mixture(
            "raspberry_rum"
        )

        self.assertIn(
            "ethanol",
            rum.chemical_base
        )

        self.assertIn(
            "water",
            rum.chemical_base
        )

        self.assertGreater(
            rum.aroma_profile.amount(
                "berry"
            ),
            0.0
        )

    def test_bar_smells_of_raspberry_rum(
        self
    ):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        meeting = MeetingPlace(
            universe
        )

        self.assertNotIn(
            "raspberry_rum",
            meeting.drink_menu
        )

        self.assertNotIn(
            "raspberry_rum",
            meeting
            .how_to_mix_drinks
            .recipes
        )

        self.assertIn(
            "raspberry_rum",
            meeting
            .how_to_mix_drinks
            .hidden_recipes
        )

        self.assertEqual(
            meeting.ambient_aroma.dominant_source,
            "raspberry_rum"
        )

    def test_cat_keeps_identity_under_surface_aroma(
        self
    ):
        universe = Universe()

        cats = Cats(
            universe
        )

        cat = cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short"
        )

        cats.add_surface_aroma(
            cat=cat,
            source="raspberry_rum",
            components=(
                AromaComposition.from_pairs(
                    ("berry", 1.0),
                    ("ethanol", 0.7),
                )
            ),
            intensity=0.8
        )

        current = cats.current_aroma(
            cat
        )

        self.assertGreater(
            current.amount("cat"),
            0.0
        )

        self.assertGreater(
            current.amount("berry"),
            0.0
        )

        self.assertEqual(
            cat.aroma.identity,
            "cat:pazuzu"
        )

    def test_surface_aroma_fades(
        self
    ):
        profile = AromaProfile(
            identity="test",
            base_components=AromaComposition.from_pairs(("cat", 1.0)),
        )

        profile.add_surface(
            source="fish",
            components=AromaComposition.from_pairs(("fish", 1.0)),
            intensity=1.0,
        )

        before = profile.current().amount("fish")

        profile.decay(ticks=10)

        after = profile.current().amount("fish")

        self.assertLess(
            after,
            before
        )


    def test_cronenberg_smells_of_ozone(
        self
    ):
        cronenberg = Cronenberg(
            error=RuntimeError("test"),
            source_component="test",
            source_operation="aroma"
        )

        aroma = cronenberg.aroma.current()

        self.assertEqual(
            cronenberg
            .aroma_chemical_marker
            .formula,
            "O3"
        )

        self.assertGreater(
            aroma.amount("ozone"),
            0.9
        )


if __name__ == "__main__":
    unittest.main()
