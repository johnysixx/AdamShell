from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class Word:
    id: str
    spoken_at: datetime

    @classmethod
    def spoken(cls):
        return cls(
            id=str(uuid4()),
            spoken_at=datetime.utcnow()
        )