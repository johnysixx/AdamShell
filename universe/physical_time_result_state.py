from dataclasses import dataclass, field
from types import MappingProxyType

from universe.atomic_time_process_state import (
    AtomicTimeProcessState,
)
from universe.atomic_time_state import (
    AtomicTimeState,
)
from universe.chemical_objects import (
    Isotope,
)
from universe.decay_state import (
    RadioactiveDecayState,
)
from universe.isotope_state import (
    IsotopeFormationState,
)
from universe.isotopes_process_state import (
    IsotopesProcessState,
)
from universe.physical_record_state import (
    AtomicTimeStandard,
    RadioactiveDecayPattern,
)
from universe.radioactive_decay_process_state import (
    RadioactiveDecayProcessState,
)


def _freeze_registry(
    registry,
    expected_type,
    label,
):
    values = dict(
        registry
    )

    for value in values.values():
        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{label} must contain "
                f"{expected_type.__name__} objects."
            )

    return MappingProxyType(
        values
    )


@dataclass(
    slots=True,
    frozen=True,
)
class IsotopeFormationResult:

    state: IsotopesProcessState
    isotopes: object
    isotope_state: IsotopeFormationState

    name: str = field(
        default="isotopes",
        init=False,
    )
    type: str = field(
        default="isotope_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            IsotopesProcessState,
        ):
            raise TypeError(
                "Isotope result state must use "
                "IsotopesProcessState."
            )

        if not isinstance(
            self.isotope_state,
            IsotopeFormationState,
        ):
            raise TypeError(
                "Isotope result formation state must "
                "use IsotopeFormationState."
            )

        object.__setattr__(
            self,
            "isotopes",
            _freeze_registry(
                self.isotopes,
                Isotope,
                "Isotope registry",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "isotopes": {
                name: isotope.to_dict()
                for name, isotope
                in self.isotopes.items()
            },
            "isotope_state": (
                self.isotope_state.to_dict()
            ),
        }


@dataclass(
    slots=True,
    frozen=True,
)
class AtomicTimeDefinitionResult:

    state: AtomicTimeProcessState
    time_standards: object
    atomic_time_state: AtomicTimeState

    name: str = field(
        default="atomic_time",
        init=False,
    )
    type: str = field(
        default="precision_time_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            AtomicTimeProcessState,
        ):
            raise TypeError(
                "Atomic time result state must use "
                "AtomicTimeProcessState."
            )

        if not isinstance(
            self.atomic_time_state,
            AtomicTimeState,
        ):
            raise TypeError(
                "Atomic time result state object must "
                "use AtomicTimeState."
            )

        object.__setattr__(
            self,
            "time_standards",
            _freeze_registry(
                self.time_standards,
                AtomicTimeStandard,
                "Atomic time standard registry",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "time_standards": {
                name: standard.to_dict()
                for name, standard
                in self.time_standards.items()
            },
            "atomic_time_state": (
                self.atomic_time_state.to_dict()
            ),
        }


@dataclass(
    slots=True,
    frozen=True,
)
class RadioactiveDecayDefinitionResult:

    state: RadioactiveDecayProcessState
    decay_patterns: object
    decay_state: RadioactiveDecayState

    name: str = field(
        default="radioactive_decay",
        init=False,
    )
    type: str = field(
        default="decay_time_layer",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            RadioactiveDecayProcessState,
        ):
            raise TypeError(
                "Radioactive decay result state must use "
                "RadioactiveDecayProcessState."
            )

        if not isinstance(
            self.decay_state,
            RadioactiveDecayState,
        ):
            raise TypeError(
                "Radioactive decay result state object "
                "must use RadioactiveDecayState."
            )

        object.__setattr__(
            self,
            "decay_patterns",
            _freeze_registry(
                self.decay_patterns,
                RadioactiveDecayPattern,
                "Decay pattern registry",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "decay_patterns": {
                name: pattern.to_dict()
                for name, pattern
                in self.decay_patterns.items()
            },
            "decay_state": (
                self.decay_state.to_dict()
            ),
        }
