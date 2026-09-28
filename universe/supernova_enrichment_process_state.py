from enum import Enum


class SupernovaEnrichmentProcessState(Enum):

    READY = "ready"
    FAILED = "failed"
    ENRICHED = "enriched"
