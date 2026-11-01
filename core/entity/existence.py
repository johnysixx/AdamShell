from dataclasses import dataclass

from core.entity.world_existence_state import (
    WorldExistenceState,
)


@dataclass(slots=True, frozen=True)
class ExistenceRemovalResult:
    world: str | None
    removed_existence_pct: float


class ExistenceResolver:

    @staticmethod
    def _get(entity, key, default=None):
        return getattr(entity, key, default)

    @staticmethod
    def _world_state(entity):
        state = getattr(
            entity,
            "existence_by_world",
            None,
        )

        if state is None:
            return WorldExistenceState()

        if not isinstance(state, WorldExistenceState):
            raise TypeError(
                "Entity existence_by_world must use "
                "WorldExistenceState."
            )

        return state

    @staticmethod
    def get_strongest_world(entity):
        state = ExistenceResolver._world_state(entity)

        return state.strongest_world(
            native_world=getattr(
                entity,
                "native_world",
                None,
            )
        )

    @staticmethod
    def remove_from_strongest_world(entity):
        state = ExistenceResolver._world_state(entity)

        strongest_world = state.strongest_world(
            native_world=getattr(
                entity,
                "native_world",
                None,
            )
        )

        if strongest_world is None:
            return ExistenceRemovalResult(
                world=None,
                removed_existence_pct=0.0,
            )

        removed_existence_pct = state.percent_in(
            strongest_world
        )

        if state.has_world(strongest_world):
            entity.existence_by_world = state.with_percent(
                strongest_world,
                0.0,
            )

        return ExistenceRemovalResult(
            world=strongest_world,
            removed_existence_pct=removed_existence_pct,
        )

    @staticmethod
    def exists_anywhere(entity):
        return (
            ExistenceResolver
            ._world_state(entity)
            .exists_anywhere()
        )
