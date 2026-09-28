from enum import Enum


class AtomicTimeProcessState(Enum):

    READY = "ready"
    DEFINED = "defined"
    FAILED = "failed"
