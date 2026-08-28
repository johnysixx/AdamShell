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


class Day0BouncerDualPresenceTests(
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

    def _get(
        self,
        key,
        default=None
    ):
        bouncer = self.bar.bouncer

        if isinstance(
            bouncer,
            dict
        ):
            return bouncer.get(
                key,
                default
            )

        return getattr(
            bouncer,
            key,
            default
        )

    def test_bouncer_is_inside_and_outside_at_same_time(
        self
    ):
        self.scene.advance_to_bouncer_knows_wager()

        self.assertEqual(
            self._get(
                "location"
            ),
            "dual_presence"
        )

        self.assertEqual(
            self._get(
                "locations"
            ),
            [
                "outside_bar",
                "inside_bar"
            ]
        )

    def test_bouncer_still_guards_entrance(
        self
    ):
        self.scene.advance_to_bouncer_knows_wager()

        self.assertTrue(
            self._get(
                "guards_entrance"
            )
        )

    def test_bouncer_is_also_present_inside(
        self
    ):
        self.scene.advance_to_bouncer_knows_wager()

        self.assertTrue(
            self._get(
                "present_in_bar"
            )
        )

    def test_serpent_explains_wager_to_bouncer(
        self
    ):
        result = (
            self.scene
            .advance_to_bouncer_knows_wager()
        )

        explanation = result[
            "explanation"
        ]

        self.assertEqual(
            explanation[
                "speaker"
            ],
            "serpent"
        )

        self.assertEqual(
            explanation[
                "listener"
            ],
            "bouncer"
        )

        self.assertEqual(
            explanation[
                "proposed_judges"
            ],
            [
                "bartender",
                "bouncer"
            ]
        )

    def test_bouncer_now_knows_wager(
        self
    ):
        self.scene.advance_to_bouncer_knows_wager()

        knowledge = self._get(
            "wager_knowledge"
        )

        self.assertTrue(
            knowledge[
                "known"
            ]
        )

        self.assertEqual(
            knowledge[
                "source"
            ],
            "serpent"
        )


if __name__ == "__main__":
    unittest.main()
