from dataclasses import dataclass, field


@dataclass(slots=True)
class FelineWisdomState:
    can_transmit_meow: bool = False
    awareness: dict = field(
        default_factory=dict
    )
    abilities: dict = field(
        default_factory=dict
    )
    transmission_history: list = field(
        default_factory=list
    )
    lesson_history: list = field(
        default_factory=list
    )

    def set_can_transmit_meow(
        self,
        enabled,
    ):
        self.can_transmit_meow = bool(
            enabled
        )

        return self
