from dataclasses import dataclass, field


@dataclass(slots=True)
class FelineAbilityMethodState:
    name: str
    teacher: str | None = None
    constraints: dict = field(
        default_factory=dict
    )
