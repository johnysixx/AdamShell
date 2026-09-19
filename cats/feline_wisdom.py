from cats.feline_wisdom_state import (
    FelineWisdomState,
)


class FelineWisdom:

    MEOW_ALLOWED_DOMAINS = frozenset({
        "physics",
        "feline",
    })

    @classmethod
    def create_state(
        cls,
        can_transmit_meow=False,
    ):
        return FelineWisdomState(
            can_transmit_meow=bool(
                can_transmit_meow
            )
        )

    @classmethod
    def ensure_state(
        cls,
        cat,
        can_transmit_meow=None,
    ):
        wisdom = getattr(
            cat,
            "feline_wisdom",
            None,
        )

        if wisdom is None:
            wisdom = cls.create_state()

            cat.feline_wisdom = wisdom

        elif not isinstance(
            wisdom,
            FelineWisdomState,
        ):
            raise TypeError(
                "Feline wisdom state must be "
                "FelineWisdomState."
            )

        if can_transmit_meow is not None:
            wisdom.set_can_transmit_meow(
                can_transmit_meow
            )

        return wisdom

    @classmethod
    def add_awareness(
        cls,
        cat,
        knowledge_name,
        domain,
        description=None,
        known_teachers=None,
    ):
        if domain not in (
            cls.MEOW_ALLOWED_DOMAINS
        ):
            raise ValueError(
                "MEOW knowledge must belong to "
                "physics or feline domain."
            )

        wisdom = cls.ensure_state(
            cat
        )

        awareness = {
            "name": knowledge_name,
            "domain": domain,
            "known_to_exist": True,
            "description": description,
            "known_teachers": list(
                known_teachers or []
            ),
            "transfer_mode":
                "awareness_only",
        }

        wisdom.awareness[
            knowledge_name
        ] = awareness

        return awareness

    @classmethod
    def learn_ability_method(
        cls,
        cat,
        ability_name,
        method_name,
        teacher_name,
        constraints=None,
    ):
        wisdom = cls.ensure_state(
            cat
        )

        ability = (
            wisdom
            .abilities
            .setdefault(
                ability_name,
                {
                    "learned": False,
                    "methods": {},
                    "can_close": False,
                },
            )
        )

        method = {
            "name": method_name,
            "teacher": teacher_name,
            "constraints": dict(
                constraints or {}
            ),
        }

        ability[
            "methods"
        ][
            method_name
        ] = method

        ability[
            "learned"
        ] = True

        return method
