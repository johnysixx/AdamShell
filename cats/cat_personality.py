from cats.cat_personality_state import (
    CatPersonalityState,
    CatPersonalityTraitAdjustedEvent,
)


class CatPersonality:

    TRAITS = (
        "curiosity",
        "courage",
        "aggression",
        "empathy",
        "patience",
    )

    DEFAULT_VALUE = 0.5

    @classmethod
    def create_state(cls):
        return CatPersonalityState()

    @classmethod
    def ensure_state(
        cls,
        cat
    ):
        personality = getattr(
            cat,
            "personality",
            None,
        )

        if personality is None:
            personality = cls.create_state()
            cat.personality = personality

        if not isinstance(
            personality,
            CatPersonalityState,
        ):
            raise TypeError(
                "Cat personality must be "
                "CatPersonalityState."
            )

        return personality

    @classmethod
    def adjust(
        cls,
        cat,
        trait,
        amount,
        source,
        day=None,
        metadata=None
    ):
        if trait not in cls.TRAITS:
            raise ValueError(
                f"Unknown cat personality trait: "
                f"{trait}"
            )

        personality = cls.ensure_state(
            cat
        )

        traits = personality.traits

        previous = float(
            getattr(
                traits,
                trait,
            )
        )

        amount = float(
            amount
        )

        current = min(
            1.0,
            max(
                0.0,
                previous + amount
            )
        )

        applied = current - previous

        setattr(
            traits,
            trait,
            current,
        )

        event = (
            CatPersonalityTraitAdjustedEvent(
                cat=cat.name,
                trait=trait,
                source=source,
                day=day,
                previous=previous,
                requested_change=amount,
                applied_change=applied,
                value=current,
                metadata=metadata or {},
            )
        )

        personality.experiences_processed += 1

        personality.record_event(
            event
        )

        return event.to_dict()

    @classmethod
    def apply_experience(
        cls,
        cat,
        source,
        changes,
        day=None,
        metadata=None
    ):
        events = []

        for trait, amount in changes.items():
            events.append(
                cls.adjust(
                    cat=cat,
                    trait=trait,
                    amount=amount,
                    source=source,
                    day=day,
                    metadata=metadata,
                )
            )

        return {
            "name": (
                "cat_personality_experience_applied"
            ),
            "cat": cat.name,
            "source": source,
            "day": day,
            "changes": dict(changes),
            "events": events,
            "applied": True,
        }

    @classmethod
    def dominant_trait(
        cls,
        cat
    ):
        personality = cls.ensure_state(
            cat
        )

        return max(
            cls.TRAITS,
            key=lambda trait: getattr(
                personality.traits,
                trait,
            ),
        )
