from dataclasses import dataclass, field

from meeting_place.bar_objects import (
    CatD20GibManifestedEvent,
)


@dataclass(slots=True, frozen=True)
class CatD20GibManifestationFailedResult:
    reason: str

    name: str = field(
        default="gib_manifestation_failed",
        init=False,
    )

    created: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

@dataclass(slots=True, frozen=True)
class CatD20GibAlreadyExistsResult:
    cat: object

    name: str = field(
        default="gib_already_exists",
        init=False,
    )

    created: bool = field(
        default=False,
        init=False,
    )

@dataclass(slots=True, frozen=True)
class CatD20GibManifestationResult:
    event: CatD20GibManifestedEvent
    cat: object
    entity: object

    def __post_init__(self):
        if not isinstance(
            self.event,
            CatD20GibManifestedEvent,
        ):
            raise TypeError(
                "Gib manifestation result "
                "requires "
                "CatD20GibManifestedEvent."
            )

    @property
    def name(self):
        return self.event.name

    @property
    def profile(self):
        return self.event.profile

    @property
    def profile_occurrence(self):
        return (
            self.event.profile_occurrence
        )

    @property
    def all_dice_rotation_requested(
        self
    ):
        return (
            self.event
            .all_dice_rotation_requested
        )

    @property
    def created(self):
        return self.event.created

    @property
    def visibility(self):
        return self.event.visibility

    @property
    def tick(self):
        return self.event.tick
