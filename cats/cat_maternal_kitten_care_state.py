from dataclasses import dataclass


@dataclass(slots=True)
class CatMaternalKittenCareState:
    care_events: int = 0
    last_care_day: int | None = None
    last_phase: str | None = None

    def record(
        self,
        day,
        phase,
    ):
        self.care_events += 1
        self.last_care_day = day
        self.last_phase = phase

        return self
