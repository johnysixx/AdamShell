from enum import Enum


class QuantumCatRouteState(Enum):

    OBSERVED = "observed"
    READY = "ready"
    TRAVELLING = "travelling"
    ARRIVED = "arrived"
    AVOIDING_OBSTACLE = "avoiding_obstacle"
    RELEASED = "released"
