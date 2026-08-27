class CatNeedSystem:

    RATES = {
        "hunger": 0.025,
        "thirst": 0.035,
        "fatigue": 0.020,
        "safety": 0.0,
        "social": 0.018,
        "curiosity": 0.015
    }

    @classmethod
    def advance(
        cls,
        cat
    ):
        needs = cat.needs

        needs["tick"] = int(
            needs.get(
                "tick",
                0
            )
        ) + 1

        for key, rate in cls.RATES.items():
            needs[key] = cls._clamp(
                float(
                    needs.get(
                        key,
                        0.0
                    )
                )
                + rate
            )

        dominant = max(
            cls.RATES,
            key=lambda key: needs[key]
        )

        needs["dominant"] = dominant

        return {
            "name": "cat_needs_advanced",
            "cat": cat.name,
            "dominant": dominant,
            "needs": dict(needs)
        }

    @classmethod
    def apply_action(
        cls,
        cat,
        intention_type
    ):
        needs = cat.needs

        if intention_type == "rest":
            needs["fatigue"] = cls._clamp(
                needs.get(
                    "fatigue",
                    0.0
                )
                - 0.35
            )

        elif intention_type in (
            "approach_cat",
            "share_legend"
        ):
            needs["social"] = cls._clamp(
                needs.get(
                    "social",
                    0.0
                )
                - 0.30
            )

        elif intention_type in (
            "wander",
            "observe",
            "explore_box"
        ):
            needs["curiosity"] = cls._clamp(
                needs.get(
                    "curiosity",
                    0.0
                )
                - 0.22
            )

        return dict(needs)

    @staticmethod
    def _clamp(
        value
    ):
        return max(
            0.0,
            min(
                1.0,
                float(value)
            )
        )
