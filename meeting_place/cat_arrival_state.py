from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CatBarArrivalResult:
    name: str
    cat: str
    entered: bool
    already_inside: bool
    alarm_before_bartender: bool | None = None
    bartender_available: bool | None = None
    bartender_responded: bool | None = None
    alarm_after_bartender: bool | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "entered",
            bool(self.entered),
        )

        object.__setattr__(
            self,
            "already_inside",
            bool(self.already_inside),
        )

        for attribute in (
            "alarm_before_bartender",
            "bartender_available",
            "bartender_responded",
            "alarm_after_bartender",
        ):
            value = getattr(
                self,
                attribute,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    attribute,
                    bool(value),
                )
