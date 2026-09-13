from copy import deepcopy
from dataclasses import dataclass, field

from idea_entities.eternal_fire_potential import EternalFirePotential


def _default_permissions():
    return {
        "can_exist_before_form": True,
        "can_influence": True,
        "can_become_process": True,
    }


@dataclass(slots=True)
class IdeaEntitiesState:

    layer_type: str = "entity_layer"
    status: str = "created"
    idea_entities: list = field(default_factory=list)
    eternal_fire: EternalFirePotential = field(
        default_factory=EternalFirePotential
    )
    events: list = field(default_factory=list)
    event_history: list = field(default_factory=list)
    permissions: dict = field(
        default_factory=_default_permissions
    )
    tick_count: int = 0

    def to_dict(self):
        return {
            "type": self.layer_type,
            "state": self.status,
            "idea_entities": list(self.idea_entities),
            "eternal_fire": self.eternal_fire.to_dict(),
            "events": deepcopy(self.events),
            "event_history": deepcopy(self.event_history),
            "permissions": dict(self.permissions),
            "tick_count": self.tick_count,
        }
