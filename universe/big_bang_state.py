from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from universe.big_bang_process_state import (
    BigBangProcessState,
)
from universe.physical_record_state import (
    CosmicHistoryEvent,
)
from universe.primordial_objects import (
    PrimordialEnergy,
    PrimordialMatter,
    PrimordialElement,
)


@dataclass(slots=True)
class BigBangCosmicState:

    spacetime_expanded: bool = False
    primordial_plasma_formed: bool = False
    light_nuclei_conditions_prepared: bool = False
    light_separated_from_darkness: bool = False
    darkness_present: bool = True

    def to_dict(self):
        return {
            "spacetime_expanded": (
                self.spacetime_expanded
            ),
            "primordial_plasma_formed": (
                self.primordial_plasma_formed
            ),
            "light_nuclei_conditions_prepared": (
                self.light_nuclei_conditions_prepared
            ),
            "light_separated_from_darkness": (
                self.light_separated_from_darkness
            ),
            "darkness_present": self.darkness_present,
        }

@dataclass(
    slots=True,
    frozen=True,
)
class BigBangRunResult:

    state: BigBangProcessState
    phases: tuple[CosmicHistoryEvent, ...]
    primordial_components: Mapping[str, PrimordialEnergy | PrimordialMatter]
    primordial_elements: Mapping[str, PrimordialElement]
    cosmic_state: "BigBangCosmicState"

    name: str = field(
        default="big_bang",
        init=False,
    )
    type: str = field(
        default="cosmic_origin_process",
        init=False,
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.state,
            BigBangProcessState,
        ):
            raise TypeError(
                "Big Bang result state must use "
                "BigBangProcessState."
            )

        phases = tuple(
            self.phases
        )

        for phase in phases:
            if not isinstance(
                phase,
                CosmicHistoryEvent,
            ):
                raise TypeError(
                    "Big Bang result phases must use "
                    "CosmicHistoryEvent objects."
                )

        object.__setattr__(
            self,
            "phases",
            phases,
        )

        for registry_name, accepted_types in (
            ("primordial_components", (PrimordialEnergy, PrimordialMatter)),
            ("primordial_elements", (PrimordialElement,)),
        ):
            registry = getattr(self, registry_name)

            if not isinstance(registry, Mapping):
                raise TypeError(
                    f"Big Bang {registry_name} must be a mapping."
                )

            values = dict(registry)

            for key, component in values.items():
                if not isinstance(
                    component,
                    accepted_types,
                ):
                    raise TypeError(
                        f"Big Bang {registry_name} must contain "
                        "objects of the required domain."
                    )

                if key != component.name:
                    raise ValueError(
                        f"Big Bang {registry_name} keys must "
                        "match component names."
                    )

            object.__setattr__(
                self,
                registry_name,
                MappingProxyType(values),
            )

        if not isinstance(
            self.cosmic_state,
            BigBangCosmicState,
        ):
            raise TypeError(
                "Big Bang result cosmic state must use "
                "BigBangCosmicState."
            )

    def to_dict(
        self,
    ):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "phases": [
                phase.to_dict()
                for phase in self.phases
            ],
            "primordial_components": {
                name: component.to_dict()
                for name, component
                in self.primordial_components.items()
            },
            "primordial_elements": {
                name: component.to_dict()
                for name, component
                in self.primordial_elements.items()
            },
            "cosmic_state": (
                self.cosmic_state.to_dict()
            ),
        }
