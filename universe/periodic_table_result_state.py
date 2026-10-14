from dataclasses import dataclass, field

from universe.periodic_table_process_state import (
    PeriodicTableProcessState,
)
from universe.periodic_table_state import (
    PeriodicTableRegistryState,
)


@dataclass(
    slots=True,
    frozen=True,
)
class PeriodicTableBuildResult:

    state: PeriodicTableProcessState
    registry_state: PeriodicTableRegistryState

    name: str = field(
        default="periodic_table",
        init=False,
    )
    type: str = field(
        default="element_registry",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            PeriodicTableProcessState,
        ):
            raise TypeError(
                "Periodic table result state must use "
                "PeriodicTableProcessState."
            )

        if not isinstance(
            self.registry_state,
            PeriodicTableRegistryState,
        ):
            raise TypeError(
                "Periodic table result registry state "
                "must use PeriodicTableRegistryState."
            )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "registry_state": (
                self.registry_state.to_dict()
            ),
        }
