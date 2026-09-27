from dataclasses import dataclass

from cats.duplicate_consumption_energy_resolution import (
    DuplicateConsumptionEnergyResolution,
)


@dataclass(slots=True)
class DuplicateConsumptionEnergyState:
    energy_id: str
    cat: str
    source: str
    day: int
    amount: float
    energy_kind: str
    name: str = (
        "duplicate_consumption_energy_stored"
    )
    resolved: bool = False
    resolution: (
        DuplicateConsumptionEnergyResolution
        | None
    ) = None
    energy_conserved: bool = True
    cat_d20_value: int | None = None
    resolved_entity_id: str | None = None

    def __post_init__(self):
        if (
            self.resolution is not None
            and not isinstance(
                self.resolution,
                DuplicateConsumptionEnergyResolution,
            )
        ):
            raise TypeError(
                "Duplicate consumption energy resolution "
                "must use "
                "DuplicateConsumptionEnergyResolution."
            )

    def resolve(
        self,
        resolution,
        cat_d20_value,
        resolved_entity_id=None,
    ):
        if not isinstance(
            resolution,
            DuplicateConsumptionEnergyResolution,
        ):
            raise TypeError(
                "Duplicate consumption energy resolution "
                "must use "
                "DuplicateConsumptionEnergyResolution."
            )

        self.resolved = True
        self.resolution = resolution
        self.cat_d20_value = int(
            cat_d20_value
        )
        self.resolved_entity_id = (
            resolved_entity_id
        )

        return self
