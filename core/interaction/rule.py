from dataclasses import dataclass


@dataclass
class Rule:
    name: str
    priority: int = 0
    active: bool = True

    def apply(self, universe, word):
        pass