from dataclasses import dataclass, field
from types import MappingProxyType

from universe.chemical_objects import (
    ChemicalElement,
)
from universe.heavy_element_nucleosynthesis_process_state import (
    HeavyElementNucleosynthesisProcessState,
)
from universe.heavy_element_nucleosynthesis_state import (
    HeavyElementNucleosynthesisState,
)


def _public_heavy_element_snapshot(
    element,
):
    if not isinstance(
        element,
        ChemicalElement,
    ):
        raise TypeError(
            "heavy_elements must contain "
            "ChemicalElement objects"
        )

    return {
        "name": element.name,
        "type": "element",
        "atomic_number": element.atomic_number,
        "state": element.state,
        "origin": element.origin,
        "requires": list(
            element.requires
        ),
    }


def _freeze_registry(
    registry,
):
    values = dict(
        registry
    )

    for element in values.values():
        if not isinstance(
            element,
            ChemicalElement,
        ):
            raise TypeError(
                "heavy_elements must contain "
                "ChemicalElement objects"
            )

    return MappingProxyType(
        values
    )


@dataclass(
    slots=True,
    frozen=True,
)
class HeavyElementNucleosynthesisResult:

    state: HeavyElementNucleosynthesisProcessState
    heavy_elements: object
    process_state: HeavyElementNucleosynthesisState

    name: str = field(
        default="heavy_element_nucleosynthesis",
        init=False,
    )
    type: str = field(
        default="post_iron_element_process",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            HeavyElementNucleosynthesisProcessState,
        ):
            raise TypeError(
                "Heavy element result state must use "
                "HeavyElementNucleosynthesisProcessState."
            )

        if not isinstance(
            self.process_state,
            HeavyElementNucleosynthesisState,
        ):
            raise TypeError(
                "Heavy element result process state "
                "must use "
                "HeavyElementNucleosynthesisState."
            )

        object.__setattr__(
            self,
            "heavy_elements",
            _freeze_registry(
                self.heavy_elements
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "heavy_elements": {
                name: _public_heavy_element_snapshot(
                    element
                )
                for name, element
                in self.heavy_elements.items()
            },
            "process_state": (
                self.process_state.to_dict()
            ),
        }
