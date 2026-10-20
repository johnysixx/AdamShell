from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class FelineAbilityMethodConstraints:

    requires_unlocked: bool | None = None
    opens_toward_cat: bool | None = None
    opens_away_from_cat: bool | None = None
    can_close: bool | None = None

    can_teach_meow: bool | None = None
    can_teach_owned_abilities: bool | None = None
    can_teach_to_own_kittens: bool | None = None
    can_create_foreign_teachers: bool | None = None

    can_teach_teach_other_cats: bool | None = None
    can_teach_teach_teaching: bool | None = None

    def __post_init__(
        self,
    ):
        for field_name in (
            "requires_unlocked",
            "opens_toward_cat",
            "opens_away_from_cat",
            "can_close",
            "can_teach_meow",
            "can_teach_owned_abilities",
            "can_teach_to_own_kittens",
            "can_create_foreign_teachers",
            "can_teach_teach_other_cats",
            "can_teach_teach_teaching",
        ):
            value = getattr(
                self,
                field_name,
            )

            if (
                value is not None
                and not isinstance(
                    value,
                    bool,
                )
            ):
                raise TypeError(
                    "Feline ability method "
                    f"{field_name} must be "
                    "bool or None."
                )


@dataclass(slots=True)
class FelineAbilityMethodState:

    name: str
    teacher: str | None = None

    constraints: FelineAbilityMethodConstraints = field(
        default_factory=(
            FelineAbilityMethodConstraints
        )
    )

    def __post_init__(
        self,
    ):
        self.name = str(
            self.name
        )

        if self.teacher is not None:
            self.teacher = str(
                self.teacher
            )

        if not isinstance(
            self.constraints,
            FelineAbilityMethodConstraints,
        ):
            raise TypeError(
                "Feline ability method constraints "
                "must use "
                "FelineAbilityMethodConstraints."
            )
