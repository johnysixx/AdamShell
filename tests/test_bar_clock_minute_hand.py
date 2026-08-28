import unittest

from meeting_place.bar_clock import BarClock


class BarClockMinuteHandTests(
    unittest.TestCase
):

    def test_minute_hand_moves_inside_one_bar_hour(
        self
    ):
        clock = BarClock()

        for _ in range(4):
            clock.tick()

        self.assertEqual(
            clock.time_text,
            "04:00"
        )

        clock.advance_minutes(
            20
        )

        self.assertEqual(
            clock.time_text,
            "04:20"
        )

    def test_minute_hand_completes_one_revolution(
        self
    ):
        clock = BarClock()

        clock.advance_minutes(
            59
        )

        self.assertEqual(
            clock.minute,
            59
        )

        clock.advance_minute()

        self.assertEqual(
            clock.minute,
            0
        )

        # Hour did not change.
        self.assertEqual(
            clock.hour,
            0
        )

    def test_only_tick_advances_hour(
        self
    ):
        clock = BarClock()

        clock.advance_minutes(
            42
        )

        self.assertEqual(
            clock.time_text,
            "00:42"
        )

        clock.tick()

        self.assertEqual(
            clock.time_text,
            "01:00"
        )

    def test_serpent_time_can_exist_on_clock(
        self
    ):
        clock = BarClock()

        for _ in range(4):
            clock.tick()

        clock.advance_minutes(
            20
        )

        self.assertEqual(
            clock.time_text,
            "04:20"
        )


if __name__ == "__main__":
    unittest.main()
