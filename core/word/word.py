from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class Word:
    name: str
    id: str = str(uuid4())
    spoken_at: datetime = datetime.utcnow()