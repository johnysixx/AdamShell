class BarClock:

    SECONDS_PER_HOUR = 60
    HOURS_PER_DAY = 24

    def __init__(self):
        self.tick_count = 0

    def tick(self):
        self.tick_count += 1
        return self.tick_count

    @property
    def elapsed_hours(self):
        return self.tick_count

    @property
    def elapsed_seconds(self):
        return (
            self.elapsed_hours
            * self.SECONDS_PER_HOUR
        )

    @property
    def day(self):
        return (
            self.elapsed_hours
            // self.HOURS_PER_DAY
        )

    @property
    def hour(self):
        return (
            self.elapsed_hours
            % self.HOURS_PER_DAY
        )
