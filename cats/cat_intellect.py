import random


class CatIntellect:

    MEAN_SCORE = 100.0
    STANDARD_DEVIATION = 15.0

    MINIMUM_SCORE = 40
    MAXIMUM_SCORE = 160

    @classmethod
    def create_state(
        cls,
        rng=None
    ):
        rng = rng or random

        raw_score = float(
            rng.gauss(
                cls.MEAN_SCORE,
                cls.STANDARD_DEVIATION
            )
        )

        score = int(
            round(
                min(
                    cls.MAXIMUM_SCORE,
                    max(
                        cls.MINIMUM_SCORE,
                        raw_score
                    )
                )
            )
        )

        return {
            "score": score,
            "raw_score": raw_score,
            "normalized": cls.normalize(
                score
            ),
            "distribution": "gaussian",
            "mean": cls.MEAN_SCORE,
            "standard_deviation": (
                cls.STANDARD_DEVIATION
            ),
            "minimum": cls.MINIMUM_SCORE,
            "maximum": cls.MAXIMUM_SCORE,
            "source": "natural_cat_variation"
        }

    @classmethod
    def ensure_state(
        cls,
        cat
    ):
        intellect = getattr(
            cat,
            "intellect",
            None
        )

        if intellect is None:
            intellect = cls.create_state()
            cat.intellect = intellect

        score = int(
            intellect.get(
                "score",
                cls.MEAN_SCORE
            )
        )

        score = min(
            cls.MAXIMUM_SCORE,
            max(
                cls.MINIMUM_SCORE,
                score
            )
        )

        intellect["score"] = score
        intellect["normalized"] = (
            cls.normalize(
                score
            )
        )

        intellect.setdefault(
            "distribution",
            "gaussian"
        )

        intellect.setdefault(
            "mean",
            cls.MEAN_SCORE
        )

        intellect.setdefault(
            "standard_deviation",
            cls.STANDARD_DEVIATION
        )

        intellect.setdefault(
            "minimum",
            cls.MINIMUM_SCORE
        )

        intellect.setdefault(
            "maximum",
            cls.MAXIMUM_SCORE
        )

        intellect.setdefault(
            "source",
            "natural_cat_variation"
        )

        return intellect

    @classmethod
    def normalize(
        cls,
        score
    ):
        score = float(
            score
        )

        return (
            score - cls.MINIMUM_SCORE
        ) / (
            cls.MAXIMUM_SCORE
            - cls.MINIMUM_SCORE
        )

    @classmethod
    def decision_finalist_count(
        cls,
        cat,
        candidate_count
    ):
        """
        Vyšší intelekt znamená přesnější
        zúžení rozumných možností.

        Neurčuje samotnou vůli kočky.
        """
        candidate_count = max(
            1,
            int(candidate_count)
        )

        score = cls.ensure_state(
            cat
        )["score"]

        if score >= 130:
            preferred_count = 2

        elif score >= 105:
            preferred_count = 3

        elif score >= 80:
            preferred_count = 4

        else:
            preferred_count = 5

        return min(
            candidate_count,
            preferred_count
        )

    @classmethod
    def category(
        cls,
        cat
    ):
        score = cls.ensure_state(
            cat
        )["score"]

        if score >= 130:
            return "exceptional"

        if score >= 115:
            return "high"

        if score >= 85:
            return "average"

        if score >= 70:
            return "low"

        return "very_low"