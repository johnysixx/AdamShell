from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True)
class UniverseRegistryRecord:
    id: int | float
    name: str
    type: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if type(self.id) not in (int, float):
            raise TypeError(
                "Universe registry ID must be numeric."
            )

        for field_name in ("name", "type"):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise TypeError(
                    "Universe registry record requires "
                    "nonempty name and type."
                )

        if not isinstance(self.metadata, dict):
            raise TypeError(
                "Universe metadata must be a dictionary."
            )

        self.metadata = deepcopy(self.metadata)

    def to_dict(self):
        snapshot = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
        }

        if self.metadata:
            snapshot["metadata"] = deepcopy(
                self.metadata
            )

        return snapshot


class UniverseRegistry:

    def __init__(self):
        self.universes = {
            0: UniverseRegistryRecord(
                id=0,
                name="multiverse",
                type="multiverse",
            ),
            0.5: UniverseRegistryRecord(
                id=0.5,
                name="quantum_layer",
                type="quantum_layer",
            ),
        }

        self.ids_by_name = {
            "multiverse": 0,
            "quantum_layer": 0.5
        }

        self.next_universe_id = 1

    def register_universe(self, name, universe_type="universe"):
        if name in self.ids_by_name:
            return self.ids_by_name[name]

        universe_id = self.next_universe_id

        self.universes[universe_id] = UniverseRegistryRecord(
            id=universe_id,
            name=name,
            type=universe_type,
        )

        self.ids_by_name[name] = universe_id
        self.next_universe_id += 1

        print(
            f"UNIVERSE REGISTERED: "
            f"{name} ID={universe_id}"
        )

        return universe_id
