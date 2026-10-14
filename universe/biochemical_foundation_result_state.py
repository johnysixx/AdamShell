from dataclasses import dataclass, field
from types import MappingProxyType

from universe.biochemical_foundations_process_state import (
    BiochemicalFoundationsProcessState,
)
from universe.biochemical_objects import (
    BiochemicalCompound,
)
from universe.biochemical_state import (
    BiochemicalFoundationState,
)


def _freeze_compound_registry(
    registry,
):
    values = dict(
        registry
    )

    for compound in values.values():
        if not isinstance(
            compound,
            BiochemicalCompound,
        ):
            raise TypeError(
                "Biochemical result registry must "
                "contain BiochemicalCompound objects."
            )

    return MappingProxyType(
        values
    )


@dataclass(
    slots=True,
    frozen=True,
)
class BiochemicalFoundationResult:

    state: BiochemicalFoundationsProcessState
    compounds: object
    biochemical_state: BiochemicalFoundationState

    name: str = field(
        default="biochemical_foundations",
        init=False,
    )
    type: str = field(
        default="biochemical_foundation_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            BiochemicalFoundationsProcessState,
        ):
            raise TypeError(
                "Biochemical foundation result state "
                "must use "
                "BiochemicalFoundationsProcessState."
            )

        if not isinstance(
            self.biochemical_state,
            BiochemicalFoundationState,
        ):
            raise TypeError(
                "Biochemical foundation result state "
                "object must use "
                "BiochemicalFoundationState."
            )

        object.__setattr__(
            self,
            "compounds",
            _freeze_compound_registry(
                self.compounds
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "compounds": {
                name: compound.to_dict()
                for name, compound
                in self.compounds.items()
            },
            "biochemical_state": (
                self.biochemical_state.to_dict()
            ),
        }
