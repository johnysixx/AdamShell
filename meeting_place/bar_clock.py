class BarClock:

    MINUTES_PER_HOUR = 60
    HOURS_PER_DAY = 24

    # Historical symbolic rule:
    # one bar tick == one complete bar hour.
    SECONDS_PER_HOUR = 60

    def __init__(
        self
    ):
        self.tick_count = 0

        # Position of the minute hand inside
        # the current one-hour bar tick.
        self.minute_offset = 0

    def tick(
        self
    ):
        """
        One complete bar hour passes.

        The minute hand has completed one full
        revolution during that tick and returns
        to :00 for the next hour.
        """

        self.tick_count += 1
        self.minute_offset = 0

        return self.tick_count

    def advance_minute(
        self
    ):
        """
        Move only the minute hand.

        Completing a revolution does NOT advance
        the hour. Only tick() may do that.
        """

        self.minute_offset += 1

        if (
            self.minute_offset
            >= self.MINUTES_PER_HOUR
        ):
            self.minute_offset = 0

        return self.time_text

    def advance_minutes(
        self,
        minutes
    ):
        minutes = int(
            minutes
        )

        if minutes < 0:
            raise ValueError(
                "Bar minutes cannot be negative."
            )

        for _ in range(
            minutes
        ):
            self.advance_minute()

        return self.time_text

    def set_minute(
        self,
        minute
    ):
        minute = int(
            minute
        )

        if not (
            0 <= minute
            < self.MINUTES_PER_HOUR
        ):
            raise ValueError(
                "Bar minute must be between "
                "0 and 59."
            )

        self.minute_offset = minute

        return self.time_text

    @property
    def elapsed_hours(
        self
    ):
        return self.tick_count

    @property
    def elapsed_seconds(
        self
    ):
        return (
            self.elapsed_hours
            * self.SECONDS_PER_HOUR
        )

    @property
    def day(
        self
    ):
        return (
            self.elapsed_hours
            // self.HOURS_PER_DAY
        )

    @property
    def hour(
        self
    ):
        return (
            self.elapsed_hours
            % self.HOURS_PER_DAY
        )

    @property
    def minute(
        self
    ):
        return self.minute_offset

    @property
    def time_text(
        self
    ):
        return (
            f"{self.hour:02d}:"
            f"{self.minute:02d}"
        )

    @property
    def public_state(
        self
    ):
        return {
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "time": self.time_text,
            "tick_count": self.tick_count
        }
