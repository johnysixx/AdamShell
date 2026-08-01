from universe.logger import UniverseLogger
from .lemonade_profile import LemonadeBatchProfile


class CronenbergPen:

    def __init__(self, universe, capacity=5):
        self.universe = universe
        self.name = "cronenberg_pen"
        self.location = "behind_bar"

        self.capacity = capacity
        self.cronenbergs = []

        self.total_lemonade_produced = 0.0
        self.processing_count = 0
        self.processing_history = []
        self.lemonade_profile_builder = LemonadeBatchProfile()

        UniverseLogger.boot("CRONENBERG PEN CREATED BEHIND THE BAR")

    def add_cronenberg(self, cronenberg):
        if cronenberg in self.cronenbergs:
            return False

        self.cronenbergs.append(cronenberg)

        cronenberg.location = "cronenberg_pen"
        cronenberg.current_layer = "meeting_place"
        cronenberg.state = "growing_in_pen"

        UniverseLogger.event(
            f"BOUNCER PLACES CRONENBERG IN PEN: {cronenberg.name}"
        )

        if len(self.cronenbergs) >= self.capacity:
            self.process_lemonade()

        return True

    def tick(self):
        for cronenberg in list(self.cronenbergs):
            tick = getattr(cronenberg, "tick_in_pen", None)

            if callable(tick):
                tick(self.universe)

    def projected_lemonade(self):
        return sum(
            float(getattr(cronenberg, "size", 1.0))
            for cronenberg in self.cronenbergs
        )

    def process_lemonade(self):
        batch = self.cronenbergs[:self.capacity]

        lemonade_amount = sum(
            float(getattr(cronenberg, "size", 1.0))
            for cronenberg in batch
        )

        batch_profile = (
            self.lemonade_profile_builder.build(
                batch
            )
        )

        batch_names = [
            cronenberg.name
            for cronenberg in batch
        ]

        for cronenberg in batch:
            cronenberg.state = "processed_into_lemonade"
            cronenberg.location = "lemonade_reservoir"

        del self.cronenbergs[:self.capacity]

        self.total_lemonade_produced += lemonade_amount
        self.processing_count += 1

        self.processing_history.append({
            "batch": self.processing_count,
            "cronenbergs": batch_names,
            "lemonade_amount": lemonade_amount,
            "lemonade_profile": batch_profile
        })

        meeting_place = getattr(self.universe, "meeting_place", None)
        if meeting_place is not None:
            meeting_place.cronenberg_lemonade_total += lemonade_amount
            meeting_place.cronenberg_processing_count += 1

            meeting_place.lemonade_reservoir.add_lemonade(
                amount_litres=lemonade_amount,
                source="lemon_courtyard",
                profile=batch_profile
            )

            meeting_place.lemonade_signs.sync_with_reservoir(
                meeting_place.lemonade_reservoir
            )
            meeting_place.cronenberg_processing_history.append({
                "batch": meeting_place.cronenberg_processing_count,
                "cronenbergs": batch_names,
                "lemonade_amount": lemonade_amount
            })

        UniverseLogger.event(
            f"CRONENBERG LEMONADE PRODUCED: "
            f"{lemonade_amount:.2f} litres "
            f"FROM={len(batch_names)} CRONENBERGS"
        )


        if not self.cronenbergs:
            meeting_place = getattr(self.universe, "meeting_place", None)
            if meeting_place is not None:
                meeting_place.restore_cronenberg_clearing()

        return lemonade_amount

    def get_status(self):
        return {
            "location": self.location,
            "count": len(self.cronenbergs),
            "capacity": self.capacity,
            "projected_lemonade": self.projected_lemonade(),
            "total_lemonade_produced": self.total_lemonade_produced,
            "processing_count": self.processing_count,
            "cronenbergs": [
                {
                    "name": cronenberg.name,
                    "age": getattr(cronenberg, "age", 0),
                    "size": getattr(cronenberg, "size", 1.0),
                    "state": getattr(cronenberg, "state", None)
                }
                for cronenberg in self.cronenbergs
            ]
        }
