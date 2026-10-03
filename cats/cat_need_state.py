from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatNeedsSnapshot:
    hunger: float
    thirst: float
    fatigue: float
    safety: float
    social: float
    curiosity: float
    dominant: str | None
    tick: int

    def __post_init__(self):
        object.__setattr__(
            self,
            "hunger",
            float(self.hunger),
        )

        object.__setattr__(
            self,
            "thirst",
            float(self.thirst),
        )

        object.__setattr__(
            self,
            "fatigue",
            float(self.fatigue),
        )

        object.__setattr__(
            self,
            "safety",
            float(self.safety),
        )

        object.__setattr__(
            self,
            "social",
            float(self.social),
        )

        object.__setattr__(
            self,
            "curiosity",
            float(self.curiosity),
        )

        if self.dominant is not None:
            object.__setattr__(
                self,
                "dominant",
                str(self.dominant),
            )

        object.__setattr__(
            self,
            "tick",
            int(self.tick),
        )

    @classmethod
    def from_state(
        cls,
        needs,
    ):
        return cls(
            hunger=getattr(
                needs,
                "hunger",
                0.0,
            ),
            thirst=getattr(
                needs,
                "thirst",
                0.0,
            ),
            fatigue=getattr(
                needs,
                "fatigue",
                0.0,
            ),
            safety=getattr(
                needs,
                "safety",
                0.0,
            ),
            social=getattr(
                needs,
                "social",
                0.0,
            ),
            curiosity=getattr(
                needs,
                "curiosity",
                0.0,
            ),
            dominant=getattr(
                needs,
                "dominant",
                None,
            ),
            tick=getattr(
                needs,
                "tick",
                0,
            ),
        )


@dataclass(slots=True, frozen=True)
class CatNeedsAdvancedResult:
    cat: str
    dominant: str
    needs: CatNeedsSnapshot

    name: str = field(
        default="cat_needs_advanced",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        object.__setattr__(
            self,
            "dominant",
            str(self.dominant),
        )

        if not isinstance(
            self.needs,
            CatNeedsSnapshot,
        ):
            raise TypeError(
                "Cat needs advanced result "
                "requires CatNeedsSnapshot."
            )
