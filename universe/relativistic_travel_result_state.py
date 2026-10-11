from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RelativisticTravelResult:
    distance_m: float
    speed_m_s: float
    speed_ratio_c: float
    lorentz_factor: float
    coordinate_time_s: float
    proper_time_s: float

    def __post_init__(self):
        for field_name in (
            "distance_m",
            "speed_m_s",
            "speed_ratio_c",
            "lorentz_factor",
            "coordinate_time_s",
            "proper_time_s",
        ):
            object.__setattr__(
                self,
                field_name,
                float(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

    def to_dict(self):
        return {
            "distance_m": self.distance_m,
            "speed_m_s": self.speed_m_s,
            "speed_ratio_c": self.speed_ratio_c,
            "lorentz_factor": self.lorentz_factor,
            "coordinate_time_s": self.coordinate_time_s,
            "proper_time_s": self.proper_time_s,
        }
