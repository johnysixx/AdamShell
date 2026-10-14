from dataclasses import dataclass, field
from types import MappingProxyType

from universe.chemical_objects import (
    ChemicalElement,
)
from universe.primordial_objects import (
    PrimordialCosmicComponent,
)
from universe.stellar_nucleosynthesis_process_state import (
    StellarNucleosynthesisProcessState,
)
from universe.stellar_nucleosynthesis_state import (
    StellarNucleosynthesisState,
)


def public_element_snapshot(
    element,
):
    if isinstance(
        element,
        PrimordialCosmicComponent,
    ):
        return element.to_dict()

    if not isinstance(
        element,
        ChemicalElement,
    ):
        raise TypeError(
            "elements_up_to_iron must contain "
            "primordial or ChemicalElement objects"
        )

    snapshot = {
        "name": element.name,
        "type": "element",
        "atomic_number": element.atomic_number,
        "state": element.state,
    }

    if element.origin is not None:
        snapshot["origin"] = element.origin

    return snapshot


def _freeze_element_registry(
    registry,
):
    values = dict(
        registry
    )

    for element in values.values():
        if not isinstance(
            element,
            (
                PrimordialCosmicComponent,
                ChemicalElement,
            ),
        ):
            raise TypeError(
                "elements_up_to_iron must contain "
                "primordial or ChemicalElement objects"
            )

    return MappingProxyType(
        values
    )


@dataclass(
    slots=True,
    frozen=True,
)
class StellarNucleosynthesisResult:

    state: StellarNucleosynthesisProcessState
    elements_up_to_iron: object
    stellar_nucleosynthesis_state: (
        StellarNucleosynthesisState
    )

    name: str = field(
        default="stellar_nucleosynthesis",
        init=False,
    )
    type: str = field(
        default="stellar_element_process",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            StellarNucleosynthesisProcessState,
        ):
            raise TypeError(
                "Stellar nucleosynthesis result state "
                "must use "
                "StellarNucleosynthesisProcessState."
            )

        if not isinstance(
            self.stellar_nucleosynthesis_state,
            StellarNucleosynthesisState,
        ):
            raise TypeError(
                "Stellar nucleosynthesis result state "
                "object must use "
                "StellarNucleosynthesisState."
            )

        object.__setattr__(
            self,
            "elements_up_to_iron",
            _freeze_element_registry(
                self.elements_up_to_iron
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "elements_up_to_iron": {
                name: public_element_snapshot(
                    element
                )
                for name, element
                in self.elements_up_to_iron.items()
            },
            "stellar_nucleosynthesis_state": (
                self
                .stellar_nucleosynthesis_state
                .to_dict()
            ),
        }
