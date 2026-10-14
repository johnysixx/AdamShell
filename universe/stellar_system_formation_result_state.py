from dataclasses import dataclass, field

from universe.stellar_system_objects import (
    StellarSystem,
)
from universe.stellar_system_state import (
    StellarSystemFormationState,
)
from universe.stellar_systems_process_state import (
    StellarSystemsProcessState,
)


def _freeze_systems(
    systems,
):
    values = tuple(
        systems
    )

    for system in values:
        if not isinstance(
            system,
            StellarSystem,
        ):
            raise TypeError(
                "Stellar system result must contain "
                "StellarSystem objects."
            )

    return values


@dataclass(
    slots=True,
    frozen=True,
)
class StellarSystemFormationResult:

    state: StellarSystemsProcessState
    systems: tuple[StellarSystem, ...]
    system_state: StellarSystemFormationState

    name: str = field(
        default="stellar_systems",
        init=False,
    )
    type: str = field(
        default="stellar_system_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            StellarSystemsProcessState,
        ):
            raise TypeError(
                "Stellar system result state must use "
                "StellarSystemsProcessState."
            )

        if not isinstance(
            self.system_state,
            StellarSystemFormationState,
        ):
            raise TypeError(
                "Stellar system result formation state "
                "must use StellarSystemFormationState."
            )

        object.__setattr__(
            self,
            "systems",
            _freeze_systems(
                self.systems
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "systems": [
                system.to_dict()
                for system in self.systems
            ],
            "system_state": (
                self.system_state.to_dict()
            ),
        }
