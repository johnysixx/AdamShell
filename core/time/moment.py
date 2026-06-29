from dataclasses import dataclass


@dataclass(frozen=True)
class Moment:
    name: str