from enum import Enum


class PlanetsProcessState(Enum):

    READY = "ready"
    FAILED = "failed"
    FORMED = "formed"
