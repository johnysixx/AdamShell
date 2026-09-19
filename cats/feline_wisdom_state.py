from dataclasses import dataclass, field

from cats.feline_awareness_state import (
    FelineAwarenessState,
)


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

    def store_awareness(
        self,
        awareness,
    ):
        if not isinstance(
            awareness,
            FelineAwarenessState,
        ):
            raise TypeError(
                "Feline awareness record must "
                "be FelineAwarenessState."
            )

        self.awareness[
            awareness.name
        ] = awareness

        return awareness

    def awareness_record(
        self,
        knowledge_name,
    ):
        awareness = self.awareness.get(
            knowledge_name
        )

        if awareness is None:
            return None

        if not isinstance(
            awareness,
            FelineAwarenessState,
        ):
            raise TypeError(
                "Feline awareness record must "
                "be FelineAwarenessState."
            )

        return awareness

    def awareness_items(
        self,
    ):
        for (
            knowledge_name,
            awareness,
        ) in self.awareness.items():

            if not isinstance(
                awareness,
                FelineAwarenessState,
            ):
                raise TypeError(
                    "Feline awareness record "
                    "must be "
                    "FelineAwarenessState."
                )

            yield (
                knowledge_name,
                awareness,
            )
