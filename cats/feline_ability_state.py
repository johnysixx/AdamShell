from dataclasses import dataclass, field

from cats.feline_ability_method_state import (
    FelineAbilityMethodState,
)


class FelineAbilityMethodRegistry:

    __slots__ = (
        "_records",
    )

    def __init__(
        self,
    ):
        self._records = []

    @property
    def is_empty(
        self,
    ):
        return not self._records

    def store(
        self,
        method,
    ):
        if not isinstance(
            method,
            FelineAbilityMethodState,
        ):
            raise TypeError(
                "Feline ability method registry "
                "requires "
                "FelineAbilityMethodState."
            )

        for index, current in enumerate(
            self._records
        ):
            if not isinstance(
                current,
                FelineAbilityMethodState,
            ):
                raise TypeError(
                    "Feline ability method registry "
                    "contains invalid runtime state."
                )

            if current.name == method.name:
                self._records[
                    index
                ] = method

                return method

        self._records.append(
            method
        )

        return method

    def record(
        self,
        method_name,
    ):
        method_name = str(
            method_name
        )

        for method in self.records():
            if method.name == method_name:
                return method

        return None

    def records(
        self,
    ):
        for method in self._records:
            if not isinstance(
                method,
                FelineAbilityMethodState,
            ):
                raise TypeError(
                    "Feline ability method registry "
                    "contains invalid runtime state."
                )

        return tuple(
            self._records
        )

    def names(
        self,
    ):
        return tuple(
            method.name
            for method
            in self.records()
        )


@dataclass(slots=True)
class FelineAbilityState:

    learned: bool = False

    methods: FelineAbilityMethodRegistry = field(
        default_factory=(
            FelineAbilityMethodRegistry
        )
    )

    can_close: bool = False

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.methods,
            FelineAbilityMethodRegistry,
        ):
            raise TypeError(
                "Feline ability methods must use "
                "FelineAbilityMethodRegistry."
            )

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

        return self.methods.store(
            method
        )

    def method_record(
        self,
        method_name,
    ):
        return self.methods.record(
            method_name
        )

    def method_records(
        self,
    ):
        return self.methods.records()

    def method_names(
        self,
    ):
        return self.methods.names()
