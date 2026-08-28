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


class Day0GarfieldOrdinaryCatArrivalTests(
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

    def _arrival(
        self
    ):
        result = (
            self.scene
            .advance_to_garfield_arrival()
        )

        return result[
            "garfield"
        ][
            "ordinary_arrival"
        ]

    def test_garfield_uses_ordinary_cat_arrival(
        self
    ):
        arrival = self._arrival()

        self.assertEqual(
            arrival[
                "name"
            ],
            "cat_arrival_completed"
        )

        self.assertEqual(
            arrival[
                "cat"
            ],
            "garfield"
        )

    def test_cat_creation_activates_normal_alarm(
        self
    ):
        arrival = self._arrival()

        self.assertTrue(
            arrival[
                "alarm_before_bartender"
            ]
        )

    def test_bartender_decides_to_respond(
        self
    ):
        arrival = self._arrival()

        self.assertTrue(
            arrival[
                "bartender_responded"
            ]
        )

        self.assertFalse(
            arrival[
                "alarm_after_bartender"
            ]
        )

    def test_garfield_enters_bar(
        self
    ):
        self.scene.advance_to_garfield_arrival()

        self.assertIn(
            self.scene.garfield,
            self.bar.entities
        )

    def test_normal_cat_entry_serves_garfield_milk(
        self
    ):
        self.scene.advance_to_garfield_arrival()

        found = False

        for event in self.bar.events:

            if (
                isinstance(
                    event,
                    str
                )
                and "garfield"
                in event
                and "drinks milk"
                in event
            ):
                found = True
                break

            if (
                isinstance(
                    event,
                    dict
                )
                and event.get(
                    "cat"
                )
                == "garfield"
                and event.get(
                    "name"
                )
                == "cat_drank_milk_at_bar"
            ):
                found = True
                break

        self.assertTrue(
            found
        )

    def test_no_garfield_specific_alarm_methods_exist(
        self
    ):
        self.assertFalse(
            hasattr(
                self.scene,
                "garfield_arrival_triggers_bar_alarm"
            )
        )

        self.assertFalse(
            hasattr(
                self.scene,
                "bartender_turns_off_bar_alarm"
            )
        )

        self.assertFalse(
            hasattr(
                self.scene,
                "bartender_handles_current_bar_alarm"
            )
        )


if __name__ == "__main__":
    unittest.main()
