import unittest

from universe.universe import Universe
from cats.cats import Cats
from universe.aroma_profile import AromaProfile
from universe.aroma_residue import AromaResidue


class AromaDecayLifecycleTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()
        self.universe.enable_quantum_layer()

        self.cats = Cats(
            self.universe
        )

        self.cat = self.cats.create_cat(
            name="pazuzu",
            color="black",
            fur_length="short"
        )

    def test_unused_box_stays_scentless(
        self
    ):
        box = (
            self.universe
            .create_quantum_box()
        )

        self.assertFalse(
            hasattr(
                box,
                "aroma"
            )
        )

        self.universe._tick_aroma_residues()

        self.assertFalse(
            hasattr(
                box,
                "aroma"
            )
        )

    def test_box_residue_fades_with_universe_aroma_tick(
        self
    ):
        box = (
            self.universe
            .create_quantum_box()
        )

        AromaResidue.transfer(
            source_profile=self.cat[
                "aroma"
            ],
            target=box,
            source_identity="pazuzu",
            fraction=0.3
        )

        before = AromaProfile.current(
            box.aroma
        )[
            "individual_cat:pazuzu"
        ]

        self.universe._tick_aroma_residues()

        after = AromaProfile.current(
            box.aroma
        )[
            "individual_cat:pazuzu"
        ]

        self.assertLess(
            after,
            before
        )

    def test_cat_surface_aroma_fades_too(
        self
    ):
        AromaProfile.add_surface(
            profile=self.cat[
                "aroma"
            ],
            source="raspberry_rum",
            components={
                "raspberry": 1.0
            },
            intensity=1.0,
            decay_rate=0.1
        )

        before = AromaProfile.current(
            self.cat["aroma"]
        )[
            "raspberry"
        ]

        self.universe._tick_aroma_residues()

        after = AromaProfile.current(
            self.cat["aroma"]
        )[
            "raspberry"
        ]

        self.assertLess(
            after,
            before
        )


if __name__ == "__main__":
    unittest.main()