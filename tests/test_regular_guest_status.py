import unittest

from universe.universe import Universe
from multiverse import UniverseRegistry
from meeting_place.meeting_place import MeetingPlace


class RegularGuestStatusTests(unittest.TestCase):

    def test_fifth_visit_marks_guest_regular_for_bar_and_bartender(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        guest = {
            "name": "newton",
            "type": "guest",
            "life_history": []
        }

        meeting_place.bouncer.allowed_guests.append(
            "newton"
        )

        for _ in range(5):
            meeting_place.add_entity(
                guest
            )

        self.assertTrue(
            meeting_place.is_regular_guest(
                "newton"
            )
        )

        self.assertIn(
            "newton",
            meeting_place
            .bartender
            .regular_guests
        )


    def test_old_visits_outside_half_year_do_not_count(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.guest_visit_history[
            "newton"
        ] = [
            0,
            181,
            182,
            183
        ]

        meeting_place.bar_clock.tick_count = (
            184 * 24
        )

        meeting_place.record_guest_visit(
            "newton"
        )

        self.assertFalse(
            meeting_place.is_regular_guest(
                "newton"
            )
        )

        self.assertNotIn(
            "newton",
            meeting_place
            .bartender
            .regular_guests
        )


    def test_regular_status_is_kept_with_two_visits_per_year(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.guest_visit_history[
            "newton"
        ] = [
            1,
            2,
            3,
            4
        ]

        meeting_place.bar_clock.tick_count = (
            5 * 24
        )

        meeting_place.record_guest_visit(
            "newton"
        )

        self.assertTrue(
            meeting_place.is_regular_guest(
                "newton"
            )
        )

        meeting_place.bar_clock.tick_count = (
            200 * 24
        )

        meeting_place.record_guest_visit(
            "newton"
        )

        meeting_place.bar_clock.tick_count = (
            300 * 24
        )

        meeting_place.record_guest_visit(
            "newton"
        )

        self.assertTrue(
            meeting_place.is_regular_guest(
                "newton"
            )
        )

        self.assertIn(
            "newton",
            meeting_place
            .bartender
            .regular_guests
        )


    def test_regular_status_expires_without_two_visits_per_year(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        meeting_place.guest_visit_history[
            "newton"
        ] = [
            1,
            2,
            3,
            4
        ]

        meeting_place.bar_clock.tick_count = (
            5 * 24
        )

        meeting_place.record_guest_visit(
            "newton"
        )

        self.assertTrue(
            meeting_place.is_regular_guest(
                "newton"
            )
        )

        meeting_place.bar_clock.tick_count = (
            200 * 24
        )

        meeting_place.record_guest_visit(
            "newton"
        )

        meeting_place.bar_clock.tick_count = (
            566 * 24
        )

        meeting_place.refresh_regular_guest_status(
            "newton"
        )

        self.assertFalse(
            meeting_place.is_regular_guest(
                "newton"
            )
        )

        self.assertNotIn(
            "newton",
            meeting_place
            .bartender
            .regular_guests
        )

    def test_losing_regular_status_does_not_forget_known_guest(
        self
    ):
        universe = Universe()
        universe.universe_registry = UniverseRegistry()

        meeting_place = MeetingPlace(
            universe
        )

        life_history = [
            {
                "event": "born",
                "place": "earth"
            }
        ]

        guest = {
            "name": "newton",
            "type": "guest",
            "life_history": life_history
        }

        meeting_place.bartender.remember_guest(
            guest
        )

        meeting_place.guest_visit_history[
            "newton"
        ] = [
            1,
            2,
            3,
            4
        ]

        meeting_place.bar_clock.tick_count = (
            5 * 24
        )

        meeting_place.record_guest_visit(
            "newton"
        )

        self.assertTrue(
            meeting_place.is_regular_guest(
                "newton"
            )
        )

        meeting_place.bar_clock.tick_count = (
            400 * 24
        )

        meeting_place.refresh_regular_guest_status(
            "newton"
        )

        self.assertFalse(
            meeting_place.is_regular_guest(
                "newton"
            )
        )

        self.assertTrue(
            meeting_place.bartender.knows_guest(
                "newton"
            )
        )

        self.assertIs(
            meeting_place
            .bartender
            .known_histories["newton"],
            life_history
        )


if __name__ == "__main__":
    unittest.main()




