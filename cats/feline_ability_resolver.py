from cats.feline_wisdom import (
    FelineWisdom
)


class FelineAbilityResolver:

    OPEN_HUMAN_DOOR = (
        "open_human_door"
    )

    PAZUZU_METHOD = (
        "hang_on_handle"
    )

    QUEEN_ELISABETH_METHOD = (
        "pull_with_paw"
    )

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def register_pazuzu_door_method(
        self,
        pazuzu
    ):
        FelineWisdom.add_awareness(
            cat=pazuzu,
            knowledge_name=(
                self.OPEN_HUMAN_DOOR
            ),
            domain="feline",
            description=(
                "Some cats can open unlocked "
                "human doors."
            ),
            known_teachers=[
                pazuzu["name"]
            ]
        )

        method = (
            FelineWisdom
            .learn_ability_method(
                cat=pazuzu,
                ability_name=(
                    self.OPEN_HUMAN_DOOR
                ),
                method_name=(
                    self.PAZUZU_METHOD
                ),
                teacher_name=None,
                constraints={
                    "requires_unlocked": True,
                    "opens_toward_cat": True,
                    "opens_away_from_cat": True,
                    "can_close": False
                }
            )
        )

        return {
            "name": (
                "pazuzu_human_door_method_registered"
            ),
            "cat": pazuzu["name"],
            "method": method
        }

    def register_queen_elisabeth_door_method(
        self,
        queen
    ):
        FelineWisdom.add_awareness(
            cat=queen,
            knowledge_name=(
                self.OPEN_HUMAN_DOOR
            ),
            domain="feline",
            description=(
                "Some cats can open unlocked "
                "human doors."
            ),
            known_teachers=[
                queen["name"]
            ]
        )

        method = (
            FelineWisdom
            .learn_ability_method(
                cat=queen,
                ability_name=(
                    self.OPEN_HUMAN_DOOR
                ),
                method_name=(
                    self.QUEEN_ELISABETH_METHOD
                ),
                teacher_name=None,
                constraints={
                    "requires_unlocked": True,
                    "opens_toward_cat": True,
                    "opens_away_from_cat": False,
                    "can_close": False
                }
            )
        )

        return {
            "name": (
                "queen_elisabeth_human_door_"
                "method_registered"
            ),
            "cat": queen["name"],
            "method": method
        }

    def transmit_meow_awareness(
        self,
        teacher,
        student
    ):
        teacher_wisdom = (
            FelineWisdom.ensure_state(
                teacher
            )
        )

        student_wisdom = (
            FelineWisdom.ensure_state(
                student
            )
        )

        if not teacher_wisdom.get(
            "can_transmit_meow",
            False
        ):
            return self._deny(
                name=(
                    "meow_awareness_"
                    "transmission_denied"
                ),
                teacher=teacher,
                student=student,
                reason=(
                    "teacher_cannot_transmit_meow"
                )
            )

        transferred = []

        for knowledge_name, knowledge in (
            teacher_wisdom[
                "awareness"
            ].items()
        ):
            domain = knowledge.get(
                "domain"
            )

            if domain not in (
                FelineWisdom
                .MEOW_ALLOWED_DOMAINS
            ):
                continue

            copied = {
                "name": knowledge_name,
                "domain": domain,
                "known_to_exist": True,
                "description": knowledge.get(
                    "description"
                ),
                "known_teachers": list(
                    knowledge.get(
                        "known_teachers",
                        []
                    )
                ),
                "transfer_mode": (
                    "awareness_only"
                )
            }

            student_wisdom[
                "awareness"
            ][
                knowledge_name
            ] = copied

            transferred.append(
                copied
            )

        event = {
            "name": (
                "meow_ability_awareness_transmitted"
            ),
            "teacher": teacher["name"],
            "student": student["name"],
            "transferred": transferred,
            "transferred_count": len(
                transferred
            ),
            "methods_transferred": 0,
            "transmitted": True
        }

        teacher_wisdom[
            "transmission_history"
        ].append(
            event
        )

        student_wisdom[
            "transmission_history"
        ].append(
            event
        )

        self._record(
            event
        )

        return event

    def teach_method(
        self,
        teacher,
        student,
        ability_name,
        method_name
    ):
        teacher_wisdom = (
            FelineWisdom.ensure_state(
                teacher
            )
        )

        teacher_ability = (
            teacher_wisdom[
                "abilities"
            ].get(
                ability_name
            )
        )

        if not teacher_ability:
            return self._deny(
                name=(
                    "feline_ability_lesson_denied"
                ),
                teacher=teacher,
                student=student,
                reason=(
                    "teacher_does_not_know_ability"
                )
            )

        teacher_method = (
            teacher_ability[
                "methods"
            ].get(
                method_name
            )
        )

        if teacher_method is None:
            return self._deny(
                name=(
                    "feline_ability_lesson_denied"
                ),
                teacher=teacher,
                student=student,
                reason=(
                    "teacher_does_not_know_method"
                )
            )

        learned_method = (
            FelineWisdom
            .learn_ability_method(
                cat=student,
                ability_name=ability_name,
                method_name=method_name,
                teacher_name=teacher["name"],
                constraints=(
                    teacher_method[
                        "constraints"
                    ]
                )
            )
        )

        event = {
            "name": (
                "feline_ability_method_learned"
            ),
            "teacher": teacher["name"],
            "student": student["name"],
            "ability": ability_name,
            "method": method_name,
            "constraints": dict(
                learned_method[
                    "constraints"
                ]
            ),
            "learned": True
        }

        FelineWisdom.ensure_state(
            student
        )[
            "lesson_history"
        ].append(
            event
        )

        self._record(
            event
        )

        return event

    def can_open_human_door(
        self,
        cat,
        locked,
        opens_toward_cat
    ):
        wisdom = FelineWisdom.ensure_state(
            cat
        )

        ability = wisdom[
            "abilities"
        ].get(
            self.OPEN_HUMAN_DOOR
        )

        if not ability or not ability.get(
            "learned",
            False
        ):
            return {
                "allowed": False,
                "reason": (
                    "human_door_ability_not_learned"
                )
            }

        if locked:
            return {
                "allowed": False,
                "reason": "door_is_locked"
            }

        usable_methods = []

        for method in ability[
            "methods"
        ].values():
            constraints = method[
                "constraints"
            ]

            if (
                opens_toward_cat
                and constraints.get(
                    "opens_toward_cat",
                    False
                )
            ):
                usable_methods.append(
                    method["name"]
                )

            if (
                not opens_toward_cat
                and constraints.get(
                    "opens_away_from_cat",
                    False
                )
            ):
                usable_methods.append(
                    method["name"]
                )

        if not usable_methods:
            return {
                "allowed": False,
                "reason": (
                    "no_learned_method_for_"
                    "door_direction"
                )
            }

        return {
            "allowed": True,
            "reason": "door_can_be_opened",
            "usable_methods": (
                usable_methods
            )
        }

    def can_close_human_door(
        self,
        cat
    ):
        return {
            "allowed": False,
            "reason": (
                "no_cat_knows_how_to_"
                "close_human_doors"
            )
        }

    def _deny(
        self,
        name,
        teacher,
        student,
        reason
    ):
        event = {
            "name": name,
            "teacher": teacher.get(
                "name"
            ),
            "student": student.get(
                "name"
            ),
            "reason": reason,
            "learned": False,
            "transmitted": False
        }

        self._record(
            event
        )

        return event

    def _record(
        self,
        event
    ):
        self.history.append(
            event
        )

        quantum_events = getattr(
            self.universe,
            "quantum_events",
            None
        )

        if quantum_events is not None:
            quantum_events.append(
                event
            )