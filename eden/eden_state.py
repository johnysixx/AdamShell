from copy import deepcopy
from dataclasses import dataclass, field


def _default_permissions():
    return {
        "can_administer": ["god"],
        "can_modify": ["god"],
    }


def _snapshot_entity(entity):
    to_dict = getattr(entity, "to_dict", None)
    if callable(to_dict):
        return to_dict()
    return deepcopy(entity)


@dataclass(slots=True)
class EdenState:

    name: str = "eden"
    layer_type: str = "sandbox"
    status: str = "initialized"
    creator: str = "god"
    created_by: str = "god"
    administrator: str = "god"
    permissions: dict = field(
        default_factory=_default_permissions
    )
    entities: list = field(default_factory=list)
    plants: list = field(default_factory=list)
    trees: list = field(default_factory=list)
    animals: list = field(default_factory=list)
    rules: list = field(default_factory=list)
    observer: object = None
    relations: list = field(default_factory=list)
    day: int = 0
    max_day: int = 7
    tick_count: int = 0

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.layer_type,
            "state": self.status,
            "creator": self.creator,
            "created_by": self.created_by,
            "administrator": self.administrator,
            "permissions": {
                name: list(entities)
                for name, entities in self.permissions.items()
            },
            "entities": [
                _snapshot_entity(entity)
                for entity in self.entities
            ],
            "plants": [
                _snapshot_entity(plant)
                for plant in self.plants
            ],
            "trees": [
                _snapshot_entity(tree)
                for tree in self.trees
            ],
            "animals": [
                _snapshot_entity(animal)
                for animal in self.animals
            ],
            "rules": list(self.rules),
            "observer": self.observer,
            "relations": list(self.relations),
            "day": self.day,
            "max_day": self.max_day,
            "tick_count": self.tick_count,
        }
