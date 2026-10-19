from dataclasses import dataclass

from core.entity.components import (
    SpatialVector3,
)
from core.entity.cronenberg_system.origin import (
    CronenbergOrigin,
)
from core.entity.cronenberg_system.quantum_links import (
    CronenbergQuantumLinkSnapshot,
)
from core.entity.cronenberg_system.traits import (
    CronenbergTraitInfluence,
    CronenbergTraitValues,
)


@dataclass(slots=True, frozen=True)
class CatCronenbergEncounterMemoryDetails:

    result: str
    size_ratio: float
    cronenberg_id: str
    cronenberg_size: float
    cronenberg_energy: float
    origin: CronenbergOrigin
    traits: CronenbergTraitValues

    trait_birth_influences: tuple[
        CronenbergTraitInfluence,
        ...
    ] = ()

    quantum_links: tuple[
        CronenbergQuantumLinkSnapshot,
        ...
    ] = ()

    detour: SpatialVector3 | None = None
    destination: object = None
    escape_chance: float | None = None
    cat_growth: float | None = None
    strength_gain: float | None = None

    def __post_init__(
        self,
    ):
        object.__setattr__(
            self,
            "result",
            str(
                self.result
            ),
        )

        object.__setattr__(
            self,
            "cronenberg_id",
            str(
                self.cronenberg_id
            ),
        )

        for field_name in (
            "size_ratio",
            "cronenberg_size",
            "cronenberg_energy",
        ):
            object.__setattr__(
                self,
                field_name,
                float(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

        for field_name in (
            "escape_chance",
            "cat_growth",
            "strength_gain",
        ):
            value = getattr(
                self,
                field_name,
            )

            if value is not None:
                object.__setattr__(
                    self,
                    field_name,
                    float(
                        value
                    ),
                )

        if not isinstance(
            self.origin,
            CronenbergOrigin,
        ):
            raise TypeError(
                "Cronenberg encounter memory "
                "origin must be CronenbergOrigin."
            )

        if not isinstance(
            self.traits,
            CronenbergTraitValues,
        ):
            raise TypeError(
                "Cronenberg encounter memory "
                "traits must be "
                "CronenbergTraitValues."
            )

        influences = tuple(
            self.trait_birth_influences
        )

        for influence in influences:
            if not isinstance(
                influence,
                CronenbergTraitInfluence,
            ):
                raise TypeError(
                    "Cronenberg encounter memory "
                    "birth influence must be "
                    "CronenbergTraitInfluence."
                )

        object.__setattr__(
            self,
            "trait_birth_influences",
            influences,
        )

        links = tuple(
            self.quantum_links
        )

        for link in links:
            if not isinstance(
                link,
                CronenbergQuantumLinkSnapshot,
            ):
                raise TypeError(
                    "Cronenberg encounter memory "
                    "quantum link must be "
                    "CronenbergQuantumLinkSnapshot."
                )

        object.__setattr__(
            self,
            "quantum_links",
            links,
        )

        if (
            self.detour is not None
            and not isinstance(
                self.detour,
                SpatialVector3,
            )
        ):
            raise TypeError(
                "Cronenberg encounter memory "
                "detour must be SpatialVector3 "
                "or None."
            )
