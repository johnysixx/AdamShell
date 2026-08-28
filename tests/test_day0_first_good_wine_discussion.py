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


class Day0FirstGoodWineDiscussionTests(
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

        self.scene.advance_to_good_drink_discussion()

    def test_lilith_drinks_first_then_serpent(
        self
    ):
        result = (
            self.scene
            .lilith_and_serpent_take_first_table_drinks()
        )

        names = [
            event[
                "name"
            ]
            for event
            in self.scene.history
        ]

        lilith_index = names.index(
            "lilith_takes_first_sip_of_lilith"
        )

        serpent_index = names.index(
            "serpent_finishes_wine_at_table"
        )

        self.assertLess(
            lilith_index,
            serpent_index
        )

        self.assertTrue(
            result[
                "serpent"
            ][
                "finished"
            ]
        )

    def test_lilith_drink_applies_its_effects_when_drunk(
        self
    ):
        energy_before = (
            self.scene.lilith.get(
                "energy_j",
                0.0
            )
        )

        will_before = (
            self.scene.lilith.get(
                "creative_will",
                0.0
            )
        )

        effects = (
            self.scene
            .lilith_order[
                "final_drink"
            ][
                "effects"
            ]
        )

        self.scene.lilith_and_serpent_take_first_table_drinks()

        self.assertEqual(
            self.scene.lilith[
                "energy_j"
            ],
            energy_before
            + effects.get(
                "energy_j",
                0.0
            )
        )

        self.assertEqual(
            self.scene.lilith[
                "creative_will"
            ],
            will_before
            + effects.get(
                "creative_will",
                0.0
            )
        )

    def test_first_wine_observation_is_fuller_flavor(
        self
    ):
        self.scene.lilith_and_serpent_take_first_table_drinks()

        observation = (
            self.scene
            .lilith_and_serpent_make_first_wine_observation()
        )

        self.assertEqual(
            observation[
                "lilith"
            ][
                "observation"
            ],
            "wine_tastes_like_water"
        )

        self.assertTrue(
            observation[
                "serpent"
            ][
                "agrees"
            ]
        )

        self.assertEqual(
            observation[
                "serpent"
            ][
                "proposal"
            ],
            "flavor_should_be_fuller"
        )

    def test_discussion_is_still_unresolved(
        self
    ):
        self.scene.lilith_and_serpent_take_first_table_drinks()

        self.scene.lilith_and_serpent_make_first_wine_observation()

        discussion = (
            self.scene
            .serpent_lilith_good_drink_discussion
        )

        self.assertFalse(
            discussion[
                "resolved"
            ]
        )

        self.assertEqual(
            len(
                discussion[
                    "ideas"
                ]
            ),
            1
        )


if __name__ == "__main__":
    unittest.main()
