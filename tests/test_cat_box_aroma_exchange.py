import unittest

from universe.universe import Universe
from cats.cats import Cats
from universe.aroma_profile import AromaProfile


class CatBoxAromaExchangeTests(
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

        self.garfield = self.cats.create_cat(
            name="garfield",
            color="orange",
            fur_length="short"
        )

        self.pazuzu["current_layer"] = (
            "meeting_place"
        )

        self.garfield["current_layer"] = (
            "meeting_place"
        )

        self.source = (
            self.universe
            .create_quantum_box(
                layer="meeting_place"
            )
        )

        self.target = (
            self.universe
            .create_quantum_box(
                layer="quantum_layer"
            )
        )

        self.universe.cat_box_transfer\
            .pair_boxes(
                self.source,
                self.target
            )

    def test_unused_box_has_no_aroma(
        self
    ):
        self.assertFalse(
            hasattr(
                self.source,
                "aroma"
            )
        )

        self.assertFalse(
            hasattr(
                self.target,
                "aroma"
            )
        )

    def test_cat_leaves_aroma_on_source_box(
        self
    ):
        self.universe.cat_box_transfer\
            .transfer_cat(
                cat=self.pazuzu,
                source_box_id=(
                    self.source.id
                ),
                target_box_id=(
                    self.target.id
                )
            )

        self.assertTrue(
            hasattr(
                self.source,
                "aroma"
            )
        )

        aroma = AromaProfile.current(
            self.source.aroma
        )

        self.assertGreater(
            aroma[
                "individual_cat:pazuzu"
            ],
            0.0
        )

    def test_next_cat_picks_up_previous_cat_scent(
        self
    ):
        self.universe.cat_box_transfer\
            .transfer_cat(
                cat=self.pazuzu,
                source_box_id=(
                    self.source.id
                ),
                target_box_id=(
                    self.target.id
                )
            )

        # Vytvoříme nový cílový box, protože
        # běžný target se při transferu spotřebuje.
        second_target = (
            self.universe
            .create_quantum_box(
                layer="quantum_layer"
            )
        )

        self.universe.cat_box_transfer\
            .pair_boxes(
                self.source,
                second_target
            )

        self.universe.cat_box_transfer\
            .transfer_cat(
                cat=self.garfield,
                source_box_id=(
                    self.source.id
                ),
                target_box_id=(
                    second_target.id
                )
            )

        aroma = AromaProfile.current(
            self.garfield[
                "aroma"
            ]
        )

        self.assertGreater(
            aroma.get(
                "individual_cat:pazuzu",
                0.0
            ),
            0.0
        )

        self.assertGreater(
            aroma.get(
                "individual_cat:garfield",
                0.0
            ),
            0.0
        )


if __name__ == "__main__":
    unittest.main()