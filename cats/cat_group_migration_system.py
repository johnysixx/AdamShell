from copy import deepcopy

from core.entity.components import (
    require_optional_spatial_vector,
)
from cats.cat_group_migration_state import (
    CatGroupMigratedEvent,
    CatGroupMigrationDeniedResult,
)


class CatGroupMigrationSystem:

    def __init__(
        self,
        group_system,
    ):
        self.group_system = group_system

    def migrate(
        self,
        group_id,
        cats,
        layer,
        location,
        position=None,
        reason="group_migration",
    ):
        position = (
            require_optional_spatial_vector(
                position,
                field_name=(
                    "cat group migration position"
                ),
            )
        )

        group = (
            self.group_system
            ._group(
                group_id
            )
        )

        if getattr(
            group,
            "dissolved",
            False,
        ):
            return (
                CatGroupMigrationDeniedResult(
                    group_id=group_id,
                    reason="group_dissolved",
                )
            )

        members = (
            self.group_system
            ._member_objects(
                group,
                cats,
            )
        )

        if not members:
            return (
                CatGroupMigrationDeniedResult(
                    group_id=group_id,
                    reason="no_members",
                )
            )

        old_layer = getattr(
            group,
            "current_layer",
            None,
        )

        old_location = getattr(
            group,
            "current_location",
            None,
        )

        for member in members:
            member.current_layer = layer
            member.location = location

            if position is not None:
                member.move_to(
                    position
                )

            member.state = (
                "migrating_with_group"
            )

        group.current_layer = layer
        group.current_location = location
        group.migration_count += 1

        event = CatGroupMigratedEvent(
            group_id=group_id,
            from_layer=old_layer,
            from_location=old_location,
            to_layer=layer,
            to_location=location,
            position=position,
            reason=reason,
            members=tuple(
                member.name
                for member in members
            ),
        )

        group.history.append(
            deepcopy(
                event
            )
        )

        for member in members:
            member.social_interactions.append(
                deepcopy(
                    event
                )
            )

        return event
