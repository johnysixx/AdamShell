from dataclasses import dataclass, field

from core.entity.components import (
    SpatialVector3,
    require_optional_spatial_vector,
)


@dataclass(slots=True, frozen=True)
class CatGroupMigrationDeniedResult:
    group_id: str
    reason: str

    name: str = field(
        default="cat_group_migration_denied",
        init=False,
    )

    migrated: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupMigratedEvent:
    group_id: str
    from_layer: object
    from_location: object
    to_layer: object
    to_location: object
    position: SpatialVector3 | None
    reason: str
    members: tuple[str, ...]

    name: str = field(
        default="cat_group_migrated",
        init=False,
    )

    migrated: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "position",
            require_optional_spatial_vector(
                self.position,
                field_name=(
                    "cat group migration position"
                ),
            ),
        )

        object.__setattr__(
            self,
            "members",
            tuple(
                self.members
            ),
        )
