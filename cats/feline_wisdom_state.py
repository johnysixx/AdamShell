from dataclasses import dataclass, field

from cats.feline_ability_state import (
    FelineAbilityState,
)
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

    def store_ability(
        self,
        ability_name,
        ability,
    ):
        if not isinstance(
            ability,
            FelineAbilityState,
        ):
            raise TypeError(
                "Feline ability record must "
                "be FelineAbilityState."
            )

        self.abilities[
            ability_name
        ] = ability

        return ability

    def ability_record(
        self,
        ability_name,
    ):
        ability = self.abilities.get(
            ability_name
        )

        if ability is None:
            return None

        if not isinstance(
            ability,
            FelineAbilityState,
        ):
            raise TypeError(
                "Feline ability record must "
                "be FelineAbilityState."
            )

        return ability

    def ensure_ability(
        self,
        ability_name,
    ):
        ability = self.ability_record(
            ability_name
        )

        if ability is None:
            ability = FelineAbilityState()

            self.store_ability(
                ability_name,
                ability,
            )

        return ability

    def ability_items(
        self,
    ):
        for (
            ability_name,
            ability,
        ) in self.abilities.items():

            if not isinstance(
                ability,
                FelineAbilityState,
            ):
                raise TypeError(
                    "Feline ability record "
                    "must be "
                    "FelineAbilityState."
                )

            yield (
                ability_name,
                ability,
            )
