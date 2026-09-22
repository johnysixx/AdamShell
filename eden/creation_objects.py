from dataclasses import dataclass


@dataclass(slots=True)
class CreationLight:
    intensity: float = 1.0
    state: str = "primordial"
    speed: int = 299792458
    constant: bool = True
    name: str | None = None
    good: bool = False

    def __post_init__(self):
        if self.intensity < 0:
            raise ValueError(
                "Light intensity must not be negative"
            )
        if self.speed <= 0:
            raise ValueError(
                "Light speed must be positive"
            )
        if not self.state:
            raise ValueError(
                "Light state must not be empty"
            )

    def name_as_day(self):
        self.name = "day"

    def mark_good(self):
        self.good = True

    def to_dict(self):
        snapshot = {
            "intensity": self.intensity,
            "state": self.state,
            "speed": self.speed,
            "constant": self.constant,
        }

        if self.name is not None:
            snapshot["name"] = self.name

        if self.good:
            snapshot["good"] = True

        return snapshot


@dataclass(frozen=True, slots=True)
class CreationDarkness:
    name: str = "night"
    state: str = "primordial"

    def to_dict(self):
        return {
            "name": self.name,
            "state": self.state,
        }


@dataclass(frozen=True, slots=True)
class CreationDayPhase:
    day: int
    state: str

    def __post_init__(self):
        if self.day < 0:
            raise ValueError(
                "Creation phase day must not be negative"
            )
        if self.state not in {
            "evening",
            "morning",
        }:
            raise ValueError(
                "Creation phase state must be evening or morning"
            )

    def to_dict(self):
        return {
            "day": self.day,
            "state": self.state,
        }


@dataclass(frozen=True, slots=True)
class CreationDayRecord:
    day: int
    name: str
    complete: bool = True

    def __post_init__(self):
        if self.day < 0:
            raise ValueError(
                "Creation day must not be negative"
            )
        if not self.name:
            raise ValueError(
                "Creation day name must not be empty"
            )

    def to_dict(self):
        return {
            "day": self.day,
            "name": self.name,
            "complete": self.complete,
        }
