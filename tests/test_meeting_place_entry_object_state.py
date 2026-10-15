import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from meeting_place.meeting_place import (
    MeetingPlace,
)
from meeting_place.meeting_place_entry_state import (
    MeetingPlaceEntryDeniedResult,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class MeetingPlaceEntryObjectStateTests(
    unittest.TestCase
):

    def setUp(self):
        self.universe = Universe()

        self.universe.universe_registry = (
            UniverseRegistry()
        )

        self.meeting = MeetingPlace(
            self.universe
        )

    def test_banned_entry_returns_object(
        self,
    ):
        guest = SimpleNamespace(
            name="banned_guest",
            type="human",
        )

        self.meeting.bar_banned_humans.add(
            guest.name
        )

        result = (
            self.meeting
            .add_entity(
                guest
            )
        )

        self.assertIsInstance(
            result,
            MeetingPlaceEntryDeniedResult,
        )

        self.assertEqual(
            result.name,
            "meeting_place_entry_denied",
        )

        self.assertEqual(
            result.entity,
            "banned_guest",
        )

        self.assertEqual(
            result.reason,
            "bar_entry_banned",
        )

        self.assertFalse(
            result.entered
        )

        self.assertNotIn(
            guest,
            self.meeting.entities,
        )

    def test_entry_denial_has_no_mapping_api(
        self,
    ):
        result = (
            MeetingPlaceEntryDeniedResult(
                entity="guest",
                reason="bar_entry_banned",
            )
        )

        for mapping_method in (
            "get",
            "keys",
            "items",
            "values",
            "update",
            "setdefault",
            "__getitem__",
            "__setitem__",
        ):
            self.assertFalse(
                hasattr(
                    result,
                    mapping_method,
                ),
                mapping_method,
            )

        with self.assertRaises(
            TypeError
        ):
            _ = result[
                "reason"
            ]

    def test_entry_denial_is_frozen(
        self,
    ):
        result = (
            MeetingPlaceEntryDeniedResult(
                entity="guest",
                reason="bar_entry_banned",
            )
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.reason = (
                "changed"
            )


if __name__ == "__main__":
    unittest.main()
