from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType

from universe.aroma_profile import AromaSurfaceResidue


def _freeze_components(components):
    return MappingProxyType({
        str(component): float(amount)
        for component, amount in dict(components).items()
    })


@dataclass(slots=True, frozen=True)
class AromaResidueTransferResult:
    transferred: bool
    source: str
    components: object
    residue: AromaSurfaceResidue | None = None
    reason: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "transferred",
            bool(self.transferred),
        )
        object.__setattr__(
            self,
            "source",
            str(self.source),
        )
        object.__setattr__(
            self,
            "components",
            _freeze_components(self.components),
        )

        if (
            self.residue is not None
            and not isinstance(
                self.residue,
                AromaSurfaceResidue,
            )
        ):
            raise TypeError(
                "Aroma residue transfer result requires "
                "an AromaSurfaceResidue object."
            )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(self.reason),
            )

    def to_dict(self):
        return {
            "transferred": self.transferred,
            "source": self.source,
            "components": deepcopy(
                dict(self.components)
            ),
            "residue": (
                self.residue.to_dict()
                if self.residue is not None
                else None
            ),
            "reason": self.reason,
        }
