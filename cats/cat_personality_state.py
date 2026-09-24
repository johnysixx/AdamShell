from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType


@dataclass(slots=True)
class CatPersonalityTraits:

    curiosity: float = 0.5
    courage: float = 0.5
    aggression: float = 0.5
    empathy: float = 0.5
    patience: float = 0.5
    sociability: float = 0.5

    def to_dict(self):
        return {
            "curiosity": self.curiosity,
            "courage": self.courage,
            "aggression": self.aggression,
            "empathy": self.empathy,
            "patience": self.patience,
            "sociability": self.sociability,
        }


@dataclass(slots=True, frozen=True)
class CatPersonalityTraitAdjustedEvent:

    cat: str
    trait: str
    source: str
    day: int | None
    previous: float
    requested_change: float
    applied_change: float
    value: float
    metadata: object = field(
        default_factory=dict
    )
    name: str = field(
        default="cat_personality_trait_adjusted",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )
        object.__setattr__(
            self,
            "trait",
            str(self.trait),
        )
        object.__setattr__(
            self,
            "source",
            str(self.source),
        )

        if self.day is not None:
            object.__setattr__(
                self,
                "day",
                int(self.day),
            )

        for field_name in (
            "previous",
            "requested_change",
            "applied_change",
            "value",
        ):
            object.__setattr__(
                self,
                field_name,
                float(
                    getattr(
                        self,
                        field_name,
                    )
                ),
            )

        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(
                deepcopy(
                    dict(
                        self.metadata or {}
                    )
                )
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "trait": self.trait,
            "source": self.source,
            "day": self.day,
            "previous": self.previous,
            "requested_change": (
                self.requested_change
            ),
            "applied_change": (
                self.applied_change
            ),
            "value": self.value,
            "metadata": deepcopy(
                dict(self.metadata)
            ),
        }


@dataclass(slots=True)
class CatPersonalityState:

    traits: CatPersonalityTraits = field(
        default_factory=CatPersonalityTraits
    )
    experiences_processed: int = 0
    history: list = field(default_factory=list)

    def record_event(
        self,
        event,
    ):
        if not isinstance(
            event,
            CatPersonalityTraitAdjustedEvent,
        ):
            raise TypeError(
                "Cat personality history requires "
                "a "
                "CatPersonalityTraitAdjustedEvent "
                "object."
            )

        self.history.append(
            event
        )

        return event

    def to_dict(self):
        return {
            "traits": self.traits.to_dict(),
            "experiences_processed": (
                self.experiences_processed
            ),
            "history": [
                event.to_dict()
                for event in self.history
            ],
        }
