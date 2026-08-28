import unittest

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
            rum["chemical_base"]
        )

        self.assertIn(
            "water",
            rum["chemical_base"]
        )

        self.assertGreater(
            rum["aroma_profile"][
                "berry"
            ],
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
            meeting.ambient_aroma[
                "dominant_source"
            ],
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
            components={
                "berry": 1.0,
                "ethanol": 0.7
            },
            intensity=0.8
        )

        current = cats.current_aroma(
            cat
        )

        self.assertGreater(
            current["cat"],
            0.0
        )

        self.assertGreater(
            current["berry"],
            0.0
        )

        self.assertEqual(
            cat.aroma["identity"],
            "cat:pazuzu"
        )

    def test_surface_aroma_fades(
        self
    ):
        profile = AromaProfile.create(
            "test",
            {"cat": 1.0}
        )

        AromaProfile.add_surface(
            profile,
            "fish",
            {"fish": 1.0},
            intensity=1.0
        )

        before = AromaProfile.current(
            profile
        )["fish"]

        AromaProfile.decay(
            profile,
            ticks=10
        )

        after = AromaProfile.current(
            profile
        )["fish"]

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

        aroma = AromaProfile.current(
            cronenberg.aroma
        )

        self.assertEqual(
            cronenberg.aroma_chemical_marker[
                "formula"
            ],
            "O3"
        )

        self.assertGreater(
            aroma["ozone"],
            0.9
        )


if __name__ == "__main__":
    unittest.main()