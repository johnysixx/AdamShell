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
            "bartender_shift_chronicle"
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
            "bartender_shift_chronicle"
        )

        event = (
            entry["events"][0]
        )

        self.assertEqual(
            event["subject"],
            "guest_1"
        )

        self.assertEqual(
            event["observed_reason"],
            "unauthorized_area"
        )

        self.assertEqual(
            event["observed_outcome"],
            "ejected"
        )



    def test_bartender_chronicles_are_numbered_by_bar_day(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.bartender.observe_event(
            "first shift event"
        )

        for _ in range(24):
            meeting_place.tick()

        meeting_place.bartender.observe_event(
            "second shift event"
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
            2
        )

        self.assertEqual(
            entries[0]["bar_day"],
            1
        )

        self.assertEqual(
            entries[1]["bar_day"],
            2
        )

        self.assertEqual(
            entries[0]["events"][0][
                "observed_event"
            ],
            "first shift event"
        )

        self.assertEqual(
            entries[1]["events"][0][
                "observed_event"
            ],
            "second shift event"
        )
    def test_shift_chronicle_records_tick_range(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.bartender.observe_event(
            "shift event"
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

        chronicle = entries[0]

        self.assertEqual(
            chronicle["shift_start_tick"],
            0
        )

        self.assertEqual(
            chronicle["shift_end_tick"],
            24
        )


    def test_consecutive_shift_chronicles_have_continuous_tick_ranges(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.bartender.observe_event(
            "first shift event"
        )

        for _ in range(24):
            meeting_place.tick()

        meeting_place.bartender.observe_event(
            "second shift event"
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
            entries[0]["shift_start_tick"],
            0
        )

        self.assertEqual(
            entries[0]["shift_end_tick"],
            24
        )

        self.assertEqual(
            entries[1]["shift_start_tick"],
            24
        )

        self.assertEqual(
            entries[1]["shift_end_tick"],
            48
        )


    def test_new_bar_drink_is_noted_by_bartender(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        drink = {
            "name": "absinthe",
            "type": "bar_drink"
        }

        meeting_place.add_drink(
            drink=drink,
            source="new_bottle"
        )

        self.assertIs(
            meeting_place.drink_menu[
                "absinthe"
            ],
            drink
        )

        self.assertEqual(
            len(
                meeting_place
                .bartender
                .chronicle_memory
            ),
            1
        )

        note = (
            meeting_place
            .bartender
            .chronicle_memory[0]
        )

        self.assertEqual(
            note["kind"],
            "new_drink"
        )

        self.assertEqual(
            note["drink"],
            "absinthe"
        )

        self.assertEqual(
            note["source"],
            "new_bottle"
        )


    def test_new_bar_drink_is_written_to_shift_chronicle(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.add_drink(
            drink={
                "name": "absinthe",
                "type": "bar_drink"
            },
            source="new_bottle"
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

        chronicle = entries[0]

        self.assertEqual(
            chronicle["bar_day"],
            1
        )

        self.assertEqual(
            len(
                chronicle["events"]
            ),
            1
        )

        event = (
            chronicle["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "new_drink"
        )

        self.assertEqual(
            event["drink"],
            "absinthe"
        )

        self.assertEqual(
            event["source"],
            "new_bottle"
        )


    def test_new_bar_drink_is_written_to_shift_chronicle(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.add_drink(
            drink={
                "name": "absinthe",
                "type": "bar_drink"
            },
            source="new_bottle"
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

        chronicle = entries[0]

        self.assertEqual(
            chronicle["bar_day"],
            1
        )

        self.assertEqual(
            len(
                chronicle["events"]
            ),
            1
        )

        event = (
            chronicle["events"][0]
        )

        self.assertEqual(
            event["kind"],
            "new_drink"
        )

        self.assertEqual(
            event["drink"],
            "absinthe"
        )

        self.assertEqual(
            event["source"],
            "new_bottle"
        )


if __name__ == "__main__":
    unittest.main()
