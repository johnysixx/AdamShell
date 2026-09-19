from dataclasses import dataclass, field


@dataclass(slots=True)
class FelineAbilityState:
    learned: bool = False
    methods: dict = field(
        default_factory=dict
    )
    can_close: bool = False

    def mark_learned(
        self,
    ):
        self.learned = True
        return self
