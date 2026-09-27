from dataclasses import dataclass

from cats.cat_distribution_status import (
    CatDistributionStatus,
)


@dataclass(slots=True)
class CatDistributionState:
    recipient: str | None = None
    status: CatDistributionStatus | None = None
    suggested_layer: str | None = None

    def __post_init__(self):
        if (
            self.status is not None
            and not isinstance(
                self.status,
                CatDistributionStatus,
            )
        ):
            raise TypeError(
                "Cat distribution status must use "
                "CatDistributionStatus."
            )
