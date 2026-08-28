import unittest

from meeting_place.bar_clock import (
    BarClock
)


class BarClockTests(unittest.TestCase):

    def test_one_bar_tick_is_one_bar_hour(
        self
    ):
        clock = BarClock()

        self.assertEqual(
            clock.tick_count,
            0
        )

        self.assertEqual(
            clock.hour,
            0
        )

        clock.tick()

        self.assertEqual(
            clock.tick_count,
            1
        )

        self.assertEqual(
            clock.hour,
            1
        )


    def test_one_bar_hour_has_sixty_bar_seconds(
        self
    ):
        clock = BarClock()

        clock.tick()

        self.assertEqual(
            clock.elapsed_seconds,
            60
        )


    def test_twenty_four_ticks_make_one_bar_day(
        self
    ):
        clock = BarClock()

        for _ in range(24):
            clock.tick()

        self.assertEqual(
            clock.tick_count,
            24
        )

        self.assertEqual(
            clock.elapsed_hours,
            24
        )

        self.assertEqual(
            clock.elapsed_seconds,
            1440
        )

        self.assertEqual(
            clock.day,
            1
        )

        self.assertEqual(
            clock.hour,
            0
        )


    def test_clock_can_represent_0420_without_changing_tick_rule(
        self
    ):
        clock = BarClock()

        for _ in range(4):
            clock.tick()

        clock.advance_minutes(
            20
        )

        self.assertEqual(
            clock.hour,
            4
        )

        self.assertEqual(
            clock.minute,
            20
        )

        self.assertEqual(
            clock.time_text,
            "04:20"
        )

        clock.tick()

        self.assertEqual(
            clock.hour,
            5
        )

        # A bar tick completes the whole hour.
        # The minute hand starts the new hour at :00.
        self.assertEqual(
            clock.minute,
            0
        )

        self.assertEqual(
            clock.time_text,
            "05:00"
        )


if __name__ == "__main__":
    unittest.main()
