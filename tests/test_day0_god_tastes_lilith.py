import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.meeting_place import MeetingPlace
from library import Library
from gods import Gods
from idea_entities import IdeaEntities

from genesis.day0_first_bar_shift import (
    Day0FirstBarShift
)


class Day0GodTastesLilithTests(
    unittest.TestCase
):

    def setUp(
        self
    ):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.bar = MeetingPlace(
            self.universe
        )

        self.scene = Day0FirstBarShift(
            universe=self.universe,
            meeting_place=self.bar,
            library=Library(
                self.universe
            ),
            gods=Gods(
                self.universe
            ),
            idea_entities=IdeaEntities(
                self.universe
            )
        )

    def test_god_receives_effect_only_when_he_tastes_drink(
        self
    ):
        self.scene.advance_to_god_holding_lilith()

        energy_before = float(
            self.scene.god[
                "energy_j"
            ]
        )

        will_before = float(
            self.scene.god[
                "creative_will"
            ]
        )

        drink = (
            self.scene.god[
                "bar_state"
            ][
                "drink"
            ]
        )

        effects = drink[
            "effects"
        ]

        event = (
            self.scene
            .god_tastes_lilith()
        )

        self.assertEqual(
            self.scene.god[
                "energy_j"
            ],
            energy_before
            + float(
                effects.get(
                    "energy_j",
                    0.0
                )
            )
        )

        self.assertEqual(
            self.scene.god[
                "creative_will"
            ],
            will_before
            + float(
                effects.get(
                    "creative_will",
                    0.0
                )
            )
        )

        self.assertTrue(
            event[
                "effects_applied"
            ]
        )

    def test_god_is_now_tasting_lilith(
        self
    ):
        self.scene.advance_to_god_first_lilith_taste()

        self.assertEqual(
            self.scene.god[
                "bar_state"
            ][
                "activity"
            ],
            "tasting_lilith"
        )

        self.assertTrue(
            self.scene.god[
                "bar_state"
            ][
                "lilith_tasted"
            ]
        )

    def test_gods_bill_remains_open_and_unpaid(
        self
    ):
        result = (
            self.scene
            .advance_to_god_first_lilith_taste()
        )

        receipt = (
            result[
                "previous"
            ][
                "service"
            ][
                "receipt"
            ]
        )

        self.assertFalse(
            receipt[
                "paid"
            ]
        )

        self.assertEqual(
            receipt[
                "status"
            ],
            "open_unpaid"
        )

    def test_first_book_remains_empty_in_library(
        self
    ):
        self.scene.advance_to_god_first_lilith_taste()

        self.assertEqual(
            self.scene.first_book[
                "entries"
            ],
            []
        )

        self.assertIsNone(
            self.scene.first_book[
                "title"
            ]
        )

        self.assertEqual(
            self.scene.first_book[
                "location"
            ],
            "library"
        )

    def test_tasting_does_not_create_creator_mask(
        self
    ):
        self.scene.advance_to_god_first_lilith_taste()

        masks = self.scene.god.get(
            "masks",
            {}
        )

        self.assertNotIn(
            "creator",
            masks
        )

        self.assertNotEqual(
            self.scene.god.get(
                "active_mask"
            ),
            "creator"
        )


if __name__ == "__main__":
    unittest.main()
