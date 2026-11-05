from copy import deepcopy
from dataclasses import dataclass, field

from idea_entities.eternal_fire_potential import EternalFirePotential


@dataclass(slots=True, frozen=True)
class IdeaEntitiesPermissions:
    can_exist_before_form: bool = True
    can_influence: bool = True
    can_become_process: bool = True

    def __post_init__(self):
        for name in (
            "can_exist_before_form",
            "can_influence",
            "can_become_process",
        ):
            if type(getattr(self, name)) is not bool:
                raise TypeError(
                    "Idea entity permission flags must be bool."
                )

    def to_dict(self):
        return {
            "can_exist_before_form": self.can_exist_before_form,
            "can_influence": self.can_influence,
            "can_become_process": self.can_become_process,
        }


@dataclass(slots=True)
class IdeaEntitiesState:

    def __setattr__(self, name, value):
        if (
            name == "permissions"
            and not isinstance(
                value,
                IdeaEntitiesPermissions,
            )
        ):
            raise TypeError(
                "Idea entities permissions require "
                "IdeaEntitiesPermissions."
            )

        object.__setattr__(self, name, value)

    layer_type: str = "entity_layer"
    status: str = "created"
    idea_entities: list = field(default_factory=list)
    eternal_fire: EternalFirePotential = field(
        default_factory=EternalFirePotential
    )
    events: list = field(default_factory=list)
    event_history: list = field(default_factory=list)
    permissions: IdeaEntitiesPermissions = field(
        default_factory=IdeaEntitiesPermissions
    )
    tick_count: int = 0

    def to_dict(self):
        return {
            "type": self.layer_type,
            "state": self.status,
            "idea_entities": list(self.idea_entities),
            "eternal_fire": self.eternal_fire.to_dict(),
            "events": [
                deepcopy(event.to_dict())
                for event in self.events
            ],
            "event_history": [
                deepcopy(event.to_dict())
                for event in self.event_history
            ],
            "permissions": self.permissions.to_dict(),
            "tick_count": self.tick_count,
        }
