class TimelineBootstrap:

    def __init__(self, universe):
        self.universe = universe

    def run(self, ticks=5):
        for _ in range(ticks):
            self.universe.tick_universe()
