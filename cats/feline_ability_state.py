from dataclasses import dataclass, field

from cats.feline_ability_method_state import (
    FelineAbilityMethodState,
)


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

    def store_method(
        self,
        method,
    ):
        if not isinstance(
            method,
            FelineAbilityMethodState,
        ):
            raise TypeError(
                "Feline ability method must "
                "be FelineAbilityMethodState."
            )

        self.methods[
            method.name
        ] = method

        return method

    def method_record(
        self,
        method_name,
    ):
        method = self.methods.get(
            method_name
        )

        if method is None:
            return None

        if not isinstance(
            method,
            FelineAbilityMethodState,
        ):
            raise TypeError(
                "Feline ability method must "
                "be FelineAbilityMethodState."
            )

        return method

    def method_records(
        self,
    ):
        for method in self.methods.values():

            if not isinstance(
                method,
                FelineAbilityMethodState,
            ):
                raise TypeError(
                    "Feline ability method "
                    "must be "
                    "FelineAbilityMethodState."
                )

            yield method

    def method_names(
        self,
    ):
        return [
            method.name
            for method
            in self.method_records()
        ]
