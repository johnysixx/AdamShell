from dataclasses import dataclass
from math import isfinite

from cats.cat_need_state import (
    CatNeedsAdvancedResult,
    CatNeedsSnapshot,
)


@dataclass(frozen=True, slots=True)
class CatNeedRate:
    need: str
    increment: float

    def __post_init__(self):
        if not isinstance(self.need, str) or not self.need:
            raise TypeError("Need rate requires a name.")

        if (
            isinstance(self.increment, bool)
            or not isinstance(self.increment, (int, float))
        ):
            raise TypeError("Need rate must be numeric.")

        increment = float(self.increment)

        if not isfinite(increment) or increment < 0:
            raise ValueError(
                "Need rate must be finite and nonnegative."
            )

        object.__setattr__(
            self,
            "increment",
            increment,
        )


class CatNeedSystem:
    RATES = (
        CatNeedRate("hunger", 0.025),
        CatNeedRate("thirst", 0.035),
        CatNeedRate("fatigue", 0.02),
        CatNeedRate("safety", 0.0),
        CatNeedRate("social", 0.018),
        CatNeedRate("curiosity", 0.015),
    )

    @classmethod
    def advance(cls, cat):
        needs = cat.needs
        setattr(needs, 'tick', int(getattr(needs, 'tick', 0)) + 1)
        for rate in cls.RATES:
            setattr(
                needs,
                rate.need,
                cls._clamp(
                    float(getattr(needs, rate.need, 0.0))
                    + rate.increment
                ),
            )
        dominant = max(
            cls.RATES,
            key=lambda rate: getattr(
                needs,
                rate.need,
            ),
        ).need

        setattr(
            needs,
            "dominant",
            dominant,
        )

        snapshot = (
            CatNeedsSnapshot.from_state(
                needs
            )
        )

        return (
            CatNeedsAdvancedResult(
                cat=cat.name,
                dominant=dominant,
                needs=snapshot,
            )
        )

    @classmethod
    def apply_action(cls, cat, intention_type):
        needs = cat.needs
        if intention_type == 'rest':
            setattr(needs, 'fatigue', cls._clamp(getattr(needs, 'fatigue', 0.0) - 0.35))
        elif intention_type in ('approach_cat', 'share_legend'):
            setattr(needs, 'social', cls._clamp(getattr(needs, 'social', 0.0) - 0.3))
        elif intention_type in ('wander', 'observe', 'explore_box'):
            setattr(needs, 'curiosity', cls._clamp(getattr(needs, 'curiosity', 0.0) - 0.22))
        return (
            CatNeedsSnapshot.from_state(
                needs
            )
        )

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))
