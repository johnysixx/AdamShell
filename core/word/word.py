from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True)
class Word:
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    spoken_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
