import unittest

from meeting_place.bar_counter import BarCounter
from meeting_place.bartender import Bartender


class BartenderShiftChronicleTests(unittest.TestCase):

    def test_ejection_incident_is_written_only_at_shift_end(
        self
    ):
        bar_counter = BarCounter()

        bartender = Bartender(
            bar_counter.hidden_story_book
        )

        incident = {
            "name": "bar_security_incident",
            "category": "access_violation",
            "reason": "unauthorized_area",
            "offender": "guest_1",
            "resolved": True,
            "resolution": "ejected_and_blacklisted"
        }

        bartender.observe_event(
            incident
        )

        self.assertEqual(
            len(
                bar_counter
                .hidden_story_book
                .read_entries()
            ),
            0
        )

        bartender.end_shift()

        entries = (
            bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        self.assertEqual(
            entries[0]["type"],
            "bartender_shift_story"
        )

        self.assertEqual(
            entries[0]["subject"],
            "guest_1"
        )

        self.assertEqual(
            entries[0]["observed_outcome"],
            "ejected"
        )




