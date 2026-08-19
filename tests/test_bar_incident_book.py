import unittest

from meeting_place.bar_incident_book import BarIncidentBook


class BarIncidentBookTests(unittest.TestCase):

    def test_every_incident_can_be_recorded(
        self
    ):
        book = BarIncidentBook()

        incident = {
            "name": "bar_security_incident",
            "reason": "unknown_disturbance",
            "offender": None
        }

        entry = book.record(
            incident
        )

        self.assertEqual(
            len(book.incidents),
            1
        )

        self.assertIs(
            book.incidents[0],
            entry
        )

        self.assertEqual(
            entry["reason"],
            "unknown_disturbance"
        )


    def test_new_incident_starts_unresolved(
        self
    ):
        book = BarIncidentBook()

        incident = {
            "name": "bar_security_incident",
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
        book = BarIncidentBook()

        entry = book.record(
            {
                "name": "bar_security_incident",
                "reason": "unauthorized_area",
                "offender": "guest_1"
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


if __name__ == "__main__":
    unittest.main()


