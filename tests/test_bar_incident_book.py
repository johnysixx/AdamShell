import unittest

from meeting_place.bar_incident_book import BarIncidentBook
from meeting_place.back_room_black_box import BackRoomBlackBox


class BarIncidentBookTests(unittest.TestCase):

    def test_every_incident_can_be_recorded(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "category": "disturbance",
            "reason": "unknown_disturbance",
            "offender": None
        }

        entry = book.record(
            incident
        )

        self.assertIn(
            entry,
            book.incidents
        )

    def test_new_incident_starts_unresolved(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "category": "disturbance",
            "reason": "unknown_disturbance",
            "offender": None
        }

        entry = book.record(
            incident
        )

        self.assertFalse(
            entry["resolved"]
        )


    def test_resolved_incident_records_resolution(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        entry = book.record(
            {
                "name": "bar_security_incident",
                "category": "access_violation",
                "reason": "unauthorized_area",
                "offender": "dement"
            }
        )

        book.resolve(
            entry,
            resolution="ejected_and_blacklisted"
        )

        self.assertTrue(
            entry["resolved"]
        )

        self.assertEqual(
            entry["resolution"],
            "ejected_and_blacklisted"
        )


    def test_incident_requires_category(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "reason": "unknown_disturbance",
            "offender": None
        }

        with self.assertRaises(
            ValueError
        ):
            book.record(
                incident
            )

    def test_unknown_incident_category_is_rejected(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "category": "disturbnace",
            "reason": "unknown_disturbance",
            "offender": None
        }

        with self.assertRaises(
            ValueError
        ):
            book.record(
                incident
            )


    def test_reason_must_match_category(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "category": "medical_emergency",
            "reason": "unauthorized_area",
            "offender": "guest_1"
        }

        with self.assertRaises(
            ValueError
        ):
            book.record(
                incident
            )


    def test_incident_requires_reason(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "category": "disturbance",
            "offender": None
        }

        with self.assertRaises(
            ValueError
        ):
            book.record(
                incident
            )


    def test_incident_requires_valid_name(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "category": "disturbance",
            "reason": "unknown_disturbance",
            "offender": None
        }

        with self.assertRaises(
            ValueError
        ):
            book.record(
                incident
            )


    def test_incident_requires_offender_field(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "category": "disturbance",
            "reason": "unknown_disturbance"
        }

        with self.assertRaises(
            ValueError
        ):
            book.record(
                incident
            )


    def test_resolve_requires_nonempty_resolution(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        entry = book.record(
            {
                "name": "bar_security_incident",
                "category": "disturbance",
                "reason": "unknown_disturbance",
                "offender": None
            }
        )

        with self.assertRaises(
            ValueError
        ):
            book.resolve(
                entry,
                resolution=""
            )


    def test_unknown_resolution_is_rejected(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        entry = book.record(
            {
                "name": "bar_security_incident",
                "category": "disturbance",
                "reason": "unknown_disturbance",
                "offender": None
            }
        )

        with self.assertRaises(
            ValueError
        ):
            book.resolve(
                entry,
                resolution="bouncer_sumoned"
            )


    def test_resolution_must_match_reason(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        entry = book.record(
            {
                "name": "bar_security_incident",
                "category": "disturbance",
                "reason": "unknown_disturbance",
                "offender": None
            }
        )

        with self.assertRaises(
            ValueError
        ):
            book.resolve(
                entry,
                resolution="ejected_and_blacklisted"
            )


    def test_unauthorized_area_requires_offender(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "category": "access_violation",
            "reason": "unauthorized_area",
            "offender": None
        }

        with self.assertRaises(
            ValueError
        ):
            book.record(
                incident
            )


    def test_offender_must_be_string_or_none(
        self
    ):
        book = BarIncidentBook(
            recorder=BackRoomBlackBox()
        )

        incident = {
            "name": "bar_security_incident",
            "category": "access_violation",
            "reason": "unauthorized_area",
            "offender": 123
        }

        with self.assertRaises(
            ValueError
        ):
            book.record(
                incident
            )


    def test_record_writes_incident_to_back_room_black_box(
        self
    ):
        black_box = BackRoomBlackBox()

        book = BarIncidentBook(
            recorder=black_box
        )

        incident = {
            "name": "bar_security_incident",
            "category": "disturbance",
            "reason": "unknown_disturbance",
            "offender": None
        }

        book.record(
            incident
        )

        self.assertEqual(
            black_box.entry_count,
            1
        )

        entry = black_box.entries[0]

        self.assertEqual(
            entry["source"],
            "bar_incident_book"
        )

        self.assertEqual(
            entry["event"],
            "bar_security_incident"
        )

        self.assertEqual(
            entry["data"]["reason"],
            "unknown_disturbance"
        )


    def test_meeting_place_incident_book_uses_shared_black_box(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace

        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        meeting_place = MeetingPlace(
            universe
        )

        self.assertIs(
            meeting_place.bar_incident_book.recorder,
            meeting_place.back_room_black_box
        )


    def test_incidents_are_read_from_black_box(
        self
    ):
        black_box = BackRoomBlackBox()

        book = BarIncidentBook(
            recorder=black_box
        )

        black_box.record(
            event="bar_security_incident",
            data={
                "name": "bar_security_incident",
                "category": "disturbance",
                "reason": "unknown_disturbance",
                "offender": None,
                "resolved": False
            },
            source="bar_incident_book",
            tick=None
        )

        self.assertEqual(
            len(book.incidents),
            1
        )

        self.assertEqual(
            book.incidents[0]["reason"],
            "unknown_disturbance"
        )


    def test_incident_book_requires_recorder(
        self
    ):
        with self.assertRaises(
            TypeError
        ):
            BarIncidentBook()


    def test_real_security_incident_is_written_to_shared_black_box(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace

        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

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
            meeting_place.bar_geometry.find_cell(
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

        incident_entries = [
            entry
            for entry
            in meeting_place.back_room_black_box.entries
            if (
                entry.get("event")
                == "bar_security_incident"
            )
        ]

        self.assertEqual(
            len(incident_entries),
            1
        )

        self.assertEqual(
            incident_entries[0]["data"][
                "reason"
            ],
            "unauthorized_area"
        )

        self.assertEqual(
            incident_entries[0]["data"][
                "offender"
            ],
            "guest_1"
        )

        self.assertIs(
            meeting_place.bar_incident_book.recorder,
            meeting_place.back_room_black_box
        )


    def test_real_security_incident_reaches_bartender_event_memory(
        self
    ):
        from universe.universe import Universe
        from multiverse import UniverseRegistry
        from meeting_place.meeting_place import MeetingPlace

        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        incident = {
            "name": "bar_security_incident",
            "category": "disturbance",
            "reason": "unknown_disturbance",
            "offender": None
        }

        result = (
            meeting_place
            .bar_security_protocol
            .handle_security_incident(
                incident
            )
        )

        self.assertTrue(
            result
        )

        security_events = [
            event
            for event
            in meeting_place.bartender.event_memory
            if (
                isinstance(event, dict)
                and event.get("name")
                == "bar_security_incident"
            )
        ]

        self.assertEqual(
            len(security_events),
            1
        )


if __name__ == "__main__":
    unittest.main()
