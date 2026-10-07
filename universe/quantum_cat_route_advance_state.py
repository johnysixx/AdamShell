from dataclasses import dataclass, field

from core.entity.components import SpatialVector3
from core.entity.quantum_cat_route import (
    QuantumCatRouteEncounter,
)


@dataclass(slots=True, frozen=True)
class QuantumCatRouteNoActiveRouteResult:

    cat: str | None = None

    result: str = field(
        default="no_active_route",
        init=False,
    )

    position: None = field(
        default=None,
        init=False,
    )

    destination: None = field(
        default=None,
        init=False,
    )

    arrived: bool = field(
        default=False,
        init=False,
    )

    encounter: None = field(
        default=None,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class QuantumCatRouteAlreadyArrivedResult:

    cat: str | None
    position: SpatialVector3
    destination: object

    result: str = field(
        default="already_arrived",
        init=False,
    )

    arrived: bool = field(
        default=False,
        init=False,
    )

    encounter: None = field(
        default=None,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Already-arrived route position "
                "must be SpatialVector3."
            )


@dataclass(slots=True, frozen=True)
class QuantumCatRouteAdvancedEvent:

    cat: str | None
    position: SpatialVector3
    destination: object
    arrived: bool
    encounter: QuantumCatRouteEncounter | None = None

    result: str = field(
        default="route_advanced",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Advanced route position must "
                "be SpatialVector3."
            )

        if (
            self.encounter is not None
            and not isinstance(
                self.encounter,
                QuantumCatRouteEncounter,
            )
        ):
            raise TypeError(
                "Advanced route encounter must "
                "be QuantumCatRouteEncounter."
            )


@dataclass(slots=True, frozen=True)
class QuantumCatRouteDetouredEvent:

    cat: str | None
    position: SpatialVector3
    destination: object
    encounter: QuantumCatRouteEncounter

    result: str = field(
        default="cat_avoids_cronenberg",
        init=False,
    )

    arrived: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Route detour position must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.encounter,
            QuantumCatRouteEncounter,
        ):
            raise TypeError(
                "Route detour encounter must "
                "be QuantumCatRouteEncounter."
            )

        if (
            self.encounter.result
            != "cat_avoids_cronenberg"
        ):
            raise ValueError(
                "Route detour requires an avoided "
                "Cronenberg encounter."
            )


@dataclass(slots=True, frozen=True)
class QuantumCatRouteParadoxResult:

    cat: str | None
    blocked_by: str
    position: SpatialVector3
    destination: object
    encounter: QuantumCatRouteEncounter

    result: str = field(
        default=(
            "cat_route_paradox_created_cronenberg"
        ),
        init=False,
    )

    arrived: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.position,
            SpatialVector3,
        ):
            raise TypeError(
                "Route paradox position must "
                "be SpatialVector3."
            )

        if not isinstance(
            self.encounter,
            QuantumCatRouteEncounter,
        ):
            raise TypeError(
                "Route paradox encounter must "
                "be QuantumCatRouteEncounter."
            )


QUANTUM_CAT_ROUTE_ADVANCE_RESULT_TYPES = (
    QuantumCatRouteNoActiveRouteResult,
    QuantumCatRouteAlreadyArrivedResult,
    QuantumCatRouteAdvancedEvent,
    QuantumCatRouteDetouredEvent,
    QuantumCatRouteParadoxResult,
)
