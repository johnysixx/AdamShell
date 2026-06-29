from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Timeline:
    id: str = field(default_factory=lambda: str(uuid4()))
    parent_id: str | None = None
    name: str = "primary"