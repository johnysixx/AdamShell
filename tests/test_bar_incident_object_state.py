import unittest

from multiverse import UniverseRegistry
from universe.universe import Universe
from meeting_place.back_room_black_box import (
    BackRoomBlackBox,
    BackRoomBlackBoxEntry,
)
from meeting_place.bar_incident_book import (
    BarIncidentBook,
)
from meeting_place.bar_incident_state import (
    BarIncidentState,
)
from meeting_place.meeting_place import (
    MeetingPlace,
)


class BarIncidentObjectStateTests(
    unittest.TestCase
):

    def test_state_has_no_mapping_api(
        self
    ):
        state = BarIncidentState(
            category='disturbance',
            reason='unknown_disturbance',
            offender=None,
        )

        for name in (
            'get',
            'setdefault',
            '__getitem__',
            '__setitem__',
            'keys',
            'values',
            'items',
            'update',
        ):
            self.assertFalse(
                hasattr(
                    state,
                    name,
                )
            )

    def test_record_stores_same_object_in_recorder(
        self
    ):
        recorder = BackRoomBlackBox()

        book = BarIncidentBook(
            recorder=recorder
        )

        state = BarIncidentState(
            category='disturbance',
            reason='unknown_disturbance',
            offender=None,
        )

        returned = book.record(
            state
        )

        self.assertIs(
            returned,
            state,
        )

        self.assertIs(
            recorder.entries[0]
            .data,
            state,
        )

        self.assertIs(
            book.incidents[0],
            state,
        )

    def test_recorder_entry_is_object_state(
        self
    ):
        recorder = BackRoomBlackBox()

        state = BarIncidentState(
            category='disturbance',
            reason='unknown_disturbance',
            offender=None,
        )

        entry = recorder.record(
            event=state.name,
            data=state,
            source='bar_incident_book',
            tick=7,
        )

        self.assertIsInstance(
            entry,
            BackRoomBlackBoxEntry,
        )

        self.assertIs(
            recorder.entries[0],
            entry,
        )

        self.assertEqual(
            entry.tick,
            7,
        )

        self.assertEqual(
            entry.source,
            'bar_incident_book',
        )

        self.assertEqual(
            entry.event,
            'bar_security_incident',
        )

        self.assertIs(
            entry.data,
            state,
        )

        for mapping_method in (
            'get',
            'keys',
            'items',
            'values',
            'setdefault',
        ):
            self.assertFalse(
                hasattr(
                    entry,
                    mapping_method,
                )
            )

        with self.assertRaises(
            TypeError
        ):
            _ = entry[
                'data'
            ]

    def test_resolution_mutates_object_state(
        self
    ):
        recorder = BackRoomBlackBox()

        book = BarIncidentBook(
            recorder=recorder
        )

        state = BarIncidentState(
            category='disturbance',
            reason='unknown_disturbance',
            offender=None,
        )

        book.record(
            state
        )

        book.resolve(
            state,
            resolution='bouncer_summoned',
        )

        self.assertTrue(
            state.resolved
        )

        self.assertEqual(
            state.resolution,
            'bouncer_summoned',
        )

        self.assertIs(
            recorder.entries[0]
            .data,
            state,
        )

    def test_meeting_place_preserves_shared_incident_identity(
        self
    ):
        universe = Universe()

        universe.universe_registry = (
            UniverseRegistry()
        )

        meeting = MeetingPlace(
            universe
        )

        state = BarIncidentState(
            category='disturbance',
            reason='unknown_disturbance',
            offender=None,
        )

        returned = (
            meeting
            .bar_incident_book
            .record(
                state
            )
        )

        self.assertIs(
            returned,
            state,
        )

        self.assertIs(
            meeting.events[-1],
            state,
        )

        self.assertIs(
            meeting
            .bartender
            .event_memory[-1],
            state,
        )

        self.assertIs(
            meeting
            .back_room_black_box
            .entries[-1]
            .data,
            state,
        )

        meeting.bar_incident_book.resolve(
            state,
            resolution='bouncer_summoned',
        )

        self.assertTrue(
            meeting
            .bartender
            .event_memory[-1]
            .resolved
        )

    def test_legacy_mapping_incidents_are_rejected(
        self
    ):
        recorder = BackRoomBlackBox()

        book = BarIncidentBook(
            recorder=recorder
        )

        legacy = {
            'name':
                'bar_security_incident',
            'category':
                'disturbance',
            'reason':
                'unknown_disturbance',
            'offender':
                None,
            'resolved':
                False,
        }

        with self.assertRaises(
            TypeError
        ):
            book.record(
                legacy
            )

        recorder.record(
            event='bar_security_incident',
            data=legacy,
            source='bar_incident_book',
            tick=None,
        )

        with self.assertRaises(
            TypeError
        ):
            _ = book.incidents


if __name__ == '__main__':
    unittest.main()
