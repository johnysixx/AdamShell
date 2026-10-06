from dataclasses import dataclass, field

from cats.cat_group_threat_state import (
    CatGroupThreatResponseEvent,
)


@dataclass(slots=True, frozen=True)
class CatGroupAlliedDefenseDeniedResult:
    first_group: str
    second_group: str
    reason: str

    name: str = field(
        default="cat_group_allied_defense_denied",
        init=False,
    )

    defended: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupAlliedDefenseResult:
    first_group: str
    second_group: str
    first_response: CatGroupThreatResponseEvent
    second_response: CatGroupThreatResponseEvent

    name: str = field(
        default="cat_group_allied_defense",
        init=False,
    )

    defended: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.first_response,
            CatGroupThreatResponseEvent,
        ):
            raise TypeError(
                "First allied defense response must be "
                "CatGroupThreatResponseEvent."
            )

        if not isinstance(
            self.second_response,
            CatGroupThreatResponseEvent,
        ):
            raise TypeError(
                "Second allied defense response must be "
                "CatGroupThreatResponseEvent."
            )
