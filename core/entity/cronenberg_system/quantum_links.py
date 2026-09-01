from copy import deepcopy
from dataclasses import dataclass, field


@dataclass(slots=True)
class CronenbergQuantumLink:

    target_id: str
    link_type: str
    strength: float = 1.0
    created_tick: int | None = None
    metadata: dict = field(
        default_factory=dict
    )

    def __post_init__(self):
        self.target_id = str(self.target_id)
        self.link_type = str(self.link_type)
        self.strength = float(self.strength)
        self.metadata = deepcopy(
            self.metadata
        )

    def strengthen(self, strength):
        self.strength = max(
            self.strength,
            float(strength)
        )

    def to_dict(self):
        return {
            "target_id": self.target_id,
            "link_type": self.link_type,
            "strength": self.strength,
            "created_tick": self.created_tick,
            "metadata": deepcopy(
                self.metadata
            ),
        }


class CronenbergQuantumLinks:

    def __init__(self, owner_id):
        self.owner_id = owner_id
        self.links = []
        self.history = []

    def add_link(
        self,
        target_id,
        link_type,
        strength=1.0,
        created_tick=None,
        metadata=None
    ):
        target_id = str(target_id)
        link_type = str(link_type)
        strength = float(strength)

        existing = next(
            (
                link
                for link in self.links
                if link.target_id == target_id
                and link.link_type == link_type
            ),
            None
        )

        if existing is not None:
            existing.strengthen(
                strength
            )

            return existing.to_dict()

        link = CronenbergQuantumLink(
            target_id=target_id,
            link_type=link_type,
            strength=strength,
            created_tick=created_tick,
            metadata=metadata or {},
        )

        self.links.append(link)

        self.history.append({
            "event": "link_created",
            "link": link.to_dict()
        })

        return link.to_dict()

    def has_link_to(self, target_id):
        return any(
            link.target_id == str(target_id)
            for link in self.links
        )

    def links_to(self, target_id):
        return [
            link.to_dict()
            for link in self.links
            if link.target_id == str(target_id)
        ]

    def snapshot(self):
        return [
            link.to_dict()
            for link in self.links
        ]

    @property
    def public_state(self):
        return {
            "owner_id": self.owner_id,
            "link_count": len(self.links),
            "links": self.snapshot(),
            "history": deepcopy(
                self.history
            )
        }
