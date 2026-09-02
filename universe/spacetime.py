from dataclasses import dataclass, field


@dataclass(slots=True)
class UniverseSpacetimeTimeAxis:

    tick: int = 0
    flow: float = 1.0
    state: str = "global"

    def advance(self):
        self.tick += 1

    def to_dict(self):
        return {
            "tick": self.tick,
            "flow": self.flow,
            "state": self.state,
        }


@dataclass(slots=True)
class UniverseSpacetimeSpaceAxis:

    dimensions: int = 3
    state: str = "global"
    expanded: bool = True

    def to_dict(self):
        return {
            "dimensions": self.dimensions,
            "state": self.state,
            "expanded": self.expanded,
        }


@dataclass(slots=True)
class UniverseSpacetimeState:

    linked: bool = True
    curvature: float = 0.0
    time_axis: UniverseSpacetimeTimeAxis = field(
        default_factory=UniverseSpacetimeTimeAxis
    )
    space_axis: UniverseSpacetimeSpaceAxis = field(
        default_factory=UniverseSpacetimeSpaceAxis
    )

    def advance(self, curvature_delta=0.0):
        self.time_axis.advance()
        self.curvature += float(
            curvature_delta
        )

    def to_dict(self):
        return {
            "linked": self.linked,
            "curvature": self.curvature,
            "time_axis": (
                self.time_axis.to_dict()
            ),
            "space_axis": (
                self.space_axis.to_dict()
            ),
        }
