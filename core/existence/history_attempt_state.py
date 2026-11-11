from dataclasses import dataclass
from enum import Enum


class HistoryAttemptStatus(Enum):
    RUNNING = "running"
    IN_DOUBT = "in_doubt"


@dataclass(frozen=True, slots=True)
class HistoryAttempt:
    cycle_id: object
    branch_id: str
    status: HistoryAttemptStatus
