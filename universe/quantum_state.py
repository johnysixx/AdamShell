from dataclasses import dataclass


@dataclass(slots=True)
class UniverseQuantumState:

    enabled: bool = False
    superposition: bool = False
    observer: str | None = None
    collapsed: bool = False
    tick_count: int = 0
    collapse_count: int = 0
    last_collapse_tick: int | None = None
    uncertainty: float = 0.0
    fluctuation: float = 0.0
    entropy_delta: float = 0.0
    entropy_total: float = 0.0

    def enable(self):
        self.enabled = True

    def advance_tick(
        self,
        observer="quantum_tick",
    ):
        self.tick_count += 1
        self.collapsed = False
        self.superposition = True
        self.observer = observer
        self.fluctuation += 0.01
        self.uncertainty = (
            self.fluctuation
            * 0.5
        )
        self.entropy_delta = (
            self.uncertainty
            * 0.1
        )
        self.entropy_total += (
            self.entropy_delta
        )
        self.superposition = False
        self.collapsed = True
        self.collapse_count += 1
        self.last_collapse_tick = (
            self.tick_count
        )

    def to_dict(self):
        return {
            "enabled": self.enabled,
            "superposition": (
                self.superposition
            ),
            "observer": self.observer,
            "collapsed": self.collapsed,
            "tick_count": self.tick_count,
            "collapse_count": (
                self.collapse_count
            ),
            "last_collapse_tick": (
                self.last_collapse_tick
            ),
            "uncertainty": self.uncertainty,
            "fluctuation": self.fluctuation,
            "entropy_delta": (
                self.entropy_delta
            ),
            "entropy_total": (
                self.entropy_total
            ),
        }
