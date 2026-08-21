import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace


class BarClockIntegrationTests(unittest.TestCase):

    def test_meeting_place_tick_advances_bar_clock_one_hour(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        self.assertEqual(
            meeting_place.bar_clock.elapsed_hours,
            0
        )

        meeting_place.tick()

        self.assertEqual(
            meeting_place.bar_clock.elapsed_hours,
            1
        )


    def test_bartender_shift_ends_after_24_bar_ticks(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        incident = {
            "name": "bar_security_incident",
            "category": "access_violation",
            "reason": "unauthorized_area",
            "offender": "guest_1",
            "resolved": True,
            "resolution": "ejected_and_blacklisted"
        }

        meeting_place.bartender.observe_event(
            incident
        )

        for _ in range(23):
            meeting_place.tick()

        self.assertEqual(
            len(
                meeting_place
                .bar_counter
                .hidden_story_book
                .read_entries()
            ),
            0
        )

        meeting_place.tick()

        entries = (
            meeting_place
            .bar_counter
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
            meeting_place.bar_clock.hour,
            0
        )


    def test_real_ejection_is_written_to_bartender_story_at_shift_end(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        guest = {
            "name": "guest_1",
            "type": "guest",
            "state": "behind_bar",
            "position": {
                "x": 4000,
                "y": 0
            },
            "existence_pct": 100.0,
            "energy_j": 100.0
        }

        service = (
            meeting_place
            .bar_geometry
            .find_cell(
                name="bar_service_floor"
            )
        )

        result = (
            meeting_place
            .bar_security_protocol
            .handle_guest_entry(
                guest,
                service
            )
        )

        self.assertTrue(
            result
        )

        self.assertEqual(
            len(
                meeting_place
                .bar_counter
                .hidden_story_book
                .read_entries()
            ),
            0
        )

        for _ in range(24):
            meeting_place.tick()

        entries = (
            meeting_place
            .bar_counter
            .hidden_story_book
            .read_entries()
        )

        self.assertEqual(
            len(entries),
            1
        )

        entry = entries[0]

        self.assertEqual(
            entry["type"],
            "bartender_shift_story"
        )

        self.assertEqual(
            entry["subject"],
            "guest_1"
        )

        self.assertEqual(
            entry["observed_reason"],
            "unauthorized_area"
        )

        self.assertEqual(
            entry["observed_outcome"],
            "ejected"
        )


if __name__ == "__main__":
    unittest.main()


