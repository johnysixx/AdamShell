from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EdenPlant:
    name: str
    edible: bool = True
    forbidden: bool = False
    state: str = "alive"

    def __post_init__(self):
        if not self.name:
            raise ValueError("Plant name must not be empty")
        if not self.state:
            raise ValueError("Plant state must not be empty")

    @property
    def type(self):
        return "plant"

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "edible": self.edible,
            "forbidden": self.forbidden,
        }


@dataclass(frozen=True, slots=True)
class EdenFruitTree:
    name: str = "fruit_tree"
    fruit: bool = True
    forbidden: bool = False
    state: str = "alive"

    def __post_init__(self):
        if not self.name:
            raise ValueError("Tree name must not be empty")
        if not self.state:
            raise ValueError("Tree state must not be empty")

    @property
    def type(self):
        return "tree"

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "fruit": self.fruit,
            "forbidden": self.forbidden,
        }


@dataclass(frozen=True, slots=True)
class EdenAnimal:
    name: str
    kind: str
    forbidden: bool = False
    state: str = "alive"

    def __post_init__(self):
        if not self.name:
            raise ValueError("Animal name must not be empty")
        if self.kind not in {"air", "water", "land"}:
            raise ValueError(
                "Animal kind must be air, water, or land"
            )
        if not self.state:
            raise ValueError("Animal state must not be empty")

    @property
    def type(self):
        return "animal"

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "kind": self.kind,
            "state": self.state,
            "forbidden": self.forbidden,
        }
