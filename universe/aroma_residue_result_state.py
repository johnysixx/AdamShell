from dataclasses import dataclass

from universe.aroma_composition import (
    AromaComposition,
    require_aroma_composition,
)
from universe.aroma_profile import (
    AromaSurfaceResidue,
)


@dataclass(
    slots=True,
    frozen=True,
)
class AromaResidueTransferResult:

    transferred: bool
    source: str
    components: AromaComposition
    residue: AromaSurfaceResidue | None = None
    reason: str | None = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "transferred",
            bool(
                self.transferred
            ),
        )

        object.__setattr__(
            self,
            "source",
            str(
                self.source
            ),
        )

        object.__setattr__(
            self,
            "components",
            require_aroma_composition(
                self.components,
                field_name=(
                    "aroma residue transfer components"
                ),
            ),
        )

        if (
            self.residue is not None
            and not isinstance(
                self.residue,
                AromaSurfaceResidue,
            )
        ):
            raise TypeError(
                "Aroma residue transfer result "
                "requires an AromaSurfaceResidue "
                "object."
            )

        if self.reason is not None:
            object.__setattr__(
                self,
                "reason",
                str(
                    self.reason
                ),
            )

    def to_dict(self):
        return {
            "transferred": self.transferred,
            "source": self.source,
            "components": (
                self.components.to_dict()
            ),
            "residue": (
                self.residue.to_dict()
                if self.residue is not None
                else None
            ),
            "reason": self.reason,
        }
