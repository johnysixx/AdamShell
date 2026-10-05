from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatGroupRitualPerformanceDeniedResult:
    reason: str

    name: str = field(
        default="cat_group_ritual_denied",
        init=False,
    )

    performed: bool = field(
        default=False,
        init=False,
    )


@dataclass(slots=True, frozen=True)
class CatGroupRitualPerformedEvent:
    group_id: str
    ritual: str
    participants: tuple[str, ...]
    strength: float

    name: str = field(
        default="cat_group_ritual_performed",
        init=False,
    )

    performed: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name":
                self.name,
            "group_id":
                self.group_id,
            "ritual":
                self.ritual,
            "participants":
                list(
                    self.participants
                ),
            "strength":
                self.strength,
            "performed":
                self.performed,
        }
