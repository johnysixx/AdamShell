from dataclasses import dataclass

from cats.maternal_care_phase import (
    MaternalCarePhase,
)


@dataclass(slots=True)
class CatMaternalKittenCareState:
    care_events: int = 0
    last_care_day: int | None = None
    last_phase: MaternalCarePhase | None = None

    def __post_init__(self):
        if (
            self.last_phase is not None
            and not isinstance(
                self.last_phase,
                MaternalCarePhase,
            )
        ):
            raise TypeError(
                "Maternal kitten care phase "
                "must use MaternalCarePhase."
            )

    def record(
        self,
        day,
        phase,
    ):
        if not isinstance(
            phase,
            MaternalCarePhase,
        ):
            raise TypeError(
                "Maternal kitten care phase "
                "must use MaternalCarePhase."
            )

        self.care_events += 1
        self.last_care_day = day
        self.last_phase = phase

        return self
