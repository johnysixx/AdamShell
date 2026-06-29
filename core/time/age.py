from dataclasses import dataclass
from core.time.moment import Moment


@dataclass(frozen=True)
class Age:
    name: str
    start: Moment | None = None
    end: Moment | None = None