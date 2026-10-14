from dataclasses import dataclass, field

from universe.cosmic_objects import (
    StellarMaterialCloud,
)
from universe.stellar_objects import (
    Supernova,
)
from universe.supernova_enrichment_process_state import (
    SupernovaEnrichmentProcessState,
)
from universe.supernova_enrichment_state import (
    SupernovaEnrichmentState,
)


def _freeze_sequence(
    values,
    expected_type,
    label,
):
    items = tuple(
        values
    )

    for item in items:
        if not isinstance(
            item,
            expected_type,
        ):
            raise TypeError(
                f"{label} must contain "
                f"{expected_type.__name__} objects."
            )

    return items


@dataclass(
    slots=True,
    frozen=True,
)
class SupernovaEnrichmentResult:

    state: SupernovaEnrichmentProcessState
    supernovae: tuple[Supernova, ...]
    enriched_clouds: tuple[
        StellarMaterialCloud,
        ...,
    ]
    supernova_enrichment_state: (
        SupernovaEnrichmentState
    )

    name: str = field(
        default="supernova_enrichment",
        init=False,
    )
    type: str = field(
        default="stellar_enrichment_process",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.state,
            SupernovaEnrichmentProcessState,
        ):
            raise TypeError(
                "Supernova enrichment result state "
                "must use "
                "SupernovaEnrichmentProcessState."
            )

        if not isinstance(
            self.supernova_enrichment_state,
            SupernovaEnrichmentState,
        ):
            raise TypeError(
                "Supernova enrichment result state "
                "object must use "
                "SupernovaEnrichmentState."
            )

        object.__setattr__(
            self,
            "supernovae",
            _freeze_sequence(
                self.supernovae,
                Supernova,
                "Supernova result",
            ),
        )
        object.__setattr__(
            self,
            "enriched_clouds",
            _freeze_sequence(
                self.enriched_clouds,
                StellarMaterialCloud,
                "Enriched cloud result",
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state.value,
            "supernovae": [
                supernova.to_dict()
                for supernova in self.supernovae
            ],
            "enriched_clouds": [
                cloud.to_dict()
                for cloud in self.enriched_clouds
            ],
            "supernova_enrichment_state": (
                self.supernova_enrichment_state.to_dict()
            ),
        }
