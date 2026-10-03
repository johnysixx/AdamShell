from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatFamilyRegistrationResult:
    mother: str
    kittens: tuple[str, ...]

    name: str = field(
        default="cat_family_registered",
        init=False,
    )

    registered: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "mother",
            str(self.mother),
        )

        object.__setattr__(
            self,
            "kittens",
            tuple(
                str(kitten)
                for kitten in self.kittens
            ),
        )
