from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class MeetingPlaceEntryDeniedResult:
    entity: str | None
    reason: str

    name: str = field(
        default="meeting_place_entry_denied",
        init=False,
    )

    entered: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if self.entity is not None:
            object.__setattr__(
                self,
                "entity",
                str(
                    self.entity
                ),
            )

        object.__setattr__(
            self,
            "reason",
            str(
                self.reason
            ),
        )
