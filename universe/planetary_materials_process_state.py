from enum import Enum


class PlanetaryMaterialsProcessState(Enum):

    READY = "ready"
    FAILED = "failed"
    MATERIALIZED = "materialized"
