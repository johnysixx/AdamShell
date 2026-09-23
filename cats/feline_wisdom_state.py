from dataclasses import dataclass, field

from cats.feline_ability_state import (
    FelineAbilityState,
)
from cats.feline_awareness_state import (
    FelineAwarenessState,
)


@dataclass(slots=True, frozen=True)
class MeowFelineAwarenessTransmissionEvent:
    teacher: str
    kitten: str
    day: int
    transferred: tuple[
        FelineAwarenessState,
        ...
    ]
    name: str = field(
        default=(
            "meow_feline_awareness_transmitted"
        ),
        init=False,
    )
    ability_methods_transferred: int = field(
        default=0,
        init=False,
    )

    def __post_init__(self):
        transferred = tuple(
            self.transferred
        )

        if not all(
            isinstance(
                awareness,
                FelineAwarenessState,
            )
            for awareness in transferred
        ):
            raise TypeError(
                "Transferred feline awareness "
                "must contain "
                "FelineAwarenessState objects."
            )

        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )
        object.__setattr__(
            self,
            "kitten",
            str(self.kitten),
        )
        object.__setattr__(
            self,
            "day",
            int(self.day),
        )
        object.__setattr__(
            self,
            "transferred",
            transferred,
        )

    @property
    def transferred_count(self):
        return len(
            self.transferred
        )

    def to_dict(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "kitten": self.kitten,
            "day": self.day,
            "transferred": list(
                self.transferred
            ),
            "transferred_count": (
                self.transferred_count
            ),
            "ability_methods_transferred": (
                self.ability_methods_transferred
            ),
        }


@dataclass(slots=True, frozen=True)
class FelineAbilityAwarenessTransmissionEvent:
    teacher: str
    student: str
    transferred: tuple[
        FelineAwarenessState,
        ...
    ]
    name: str = field(
        default=(
            "meow_ability_awareness_transmitted"
        ),
        init=False,
    )
    methods_transferred: int = field(
        default=0,
        init=False,
    )
    transmitted: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        transferred = tuple(
            self.transferred
        )

        if not all(
            isinstance(
                awareness,
                FelineAwarenessState,
            )
            for awareness in transferred
        ):
            raise TypeError(
                "Transferred feline awareness "
                "must contain "
                "FelineAwarenessState objects."
            )

        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )
        object.__setattr__(
            self,
            "student",
            str(self.student),
        )
        object.__setattr__(
            self,
            "transferred",
            transferred,
        )

    @property
    def transferred_count(self):
        return len(
            self.transferred
        )

    def to_dict(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "student": self.student,
            "transferred": list(
                self.transferred
            ),
            "transferred_count": (
                self.transferred_count
            ),
            "methods_transferred": (
                self.methods_transferred
            ),
            "transmitted": self.transmitted,
        }


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

    def record_transmission(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                MeowFelineAwarenessTransmissionEvent,
                FelineAbilityAwarenessTransmissionEvent,
            ),
        ):
            raise TypeError(
                "Feline wisdom transmission "
                "history requires a feline "
                "awareness transmission "
                "event object."
            )

        self.transmission_history.append(
            event
        )

        return event

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
