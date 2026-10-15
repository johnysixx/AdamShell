import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

from meeting_place.cat_invited_guest_state import (
    CatGuestIncidentNotAttributedResult,
    CatInvitedGuestState,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)
from multiverse import UniverseRegistry
from universe.universe import Universe


class CatGuestIncidentAttributionObjectStateTests(
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

        self.human = SimpleNamespace(
            name="unattributed_human",
            type="human",
        )

    def assert_object_only(
        self,
        result,
    ):
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

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.reason = (
                "changed"
            )

    def test_incident_without_guest_record_is_object(
        self,
    ):
        result = (
            self.meeting
            .record_cat_guest_incident(
                self.human,
                category="guest_misbehavior",
            )
        )

        self.assertIsInstance(
            result,
            CatGuestIncidentNotAttributedResult,
        )

        self.assertEqual(
            result.name,
            "cat_guest_incident_not_attributed",
        )

        self.assertEqual(
            result.human,
            self.human.name,
        )

        self.assertEqual(
            result.category,
            "guest_misbehavior",
        )

        self.assertIsNone(
            result.inviting_cat
        )

        self.assertIsNone(
            result.reason
        )

        self.assertFalse(
            result.cat_responsibility
        )

        self.assertEqual(
            self.meeting.cat_guest_incidents,
            [],
        )

        self.assert_object_only(
            result
        )

    def test_missing_inviting_cat_result_is_object(
        self,
    ):
        self.meeting.cat_invited_guests = {
            self.human.name:
                CatInvitedGuestState(
                    human=self.human.name,
                    inviting_cat="missing_cat",
                    invitation_id="invitation_1",
                )
        }

        result = (
            self.meeting
            .record_cat_guest_incident(
                self.human,
                category="guest_misbehavior",
            )
        )

        self.assertIsInstance(
            result,
            CatGuestIncidentNotAttributedResult,
        )

        self.assertEqual(
            result.human,
            self.human.name,
        )

        self.assertEqual(
            result.category,
            "guest_misbehavior",
        )

        self.assertEqual(
            result.inviting_cat,
            "missing_cat",
        )

        self.assertEqual(
            result.reason,
            "inviting_cat_not_found",
        )

        self.assertFalse(
            result.cat_responsibility
        )

        self.assertEqual(
            self.meeting.cat_guest_incidents,
            [],
        )

        self.assert_object_only(
            result
        )


if __name__ == "__main__":
    unittest.main()
