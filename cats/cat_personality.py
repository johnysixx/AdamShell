class CatPersonality:

    TRAITS = (
        "curiosity",
        "courage",
        "aggression",
        "empathy",
        "patience"
    )

    DEFAULT_VALUE = 0.5

    @classmethod
    def create_state(cls):
        return {
            "traits": {
                trait: cls.DEFAULT_VALUE
                for trait in cls.TRAITS
            },
            "experiences_processed": 0,
            "history": []
        }

    @classmethod
    def ensure_state(
        cls,
        cat
    ):
        personality = cat.setdefault(
            "personality",
            cls.create_state()
        )

        traits = personality.setdefault(
            "traits",
            {}
        )

        for trait in cls.TRAITS:
            traits.setdefault(
                trait,
                cls.DEFAULT_VALUE
            )

        personality.setdefault(
            "experiences_processed",
            0
        )

        personality.setdefault(
            "history",
            []
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

        traits = personality[
            "traits"
        ]

        previous = float(
            traits[trait]
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

        traits[trait] = current

        event = {
            "name": (
                "cat_personality_trait_adjusted"
            ),
            "cat": cat.get("name"),
            "trait": trait,
            "source": source,
            "day": day,
            "previous": previous,
            "requested_change": amount,
            "applied_change": applied,
            "value": current,
            "metadata": dict(
                metadata or {}
            )
        }

        personality[
            "experiences_processed"
        ] += 1

        personality[
            "history"
        ].append(
            event
        )

        return event

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
                    metadata=metadata
                )
            )

        return {
            "name": (
                "cat_personality_experience_applied"
            ),
            "cat": cat.get("name"),
            "source": source,
            "day": day,
            "changes": dict(changes),
            "events": events,
            "applied": True
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
            personality["traits"],
            key=personality["traits"].get
        )