from cats.feline_wisdom import (
    FelineWisdom
)


class FelineTeacherResolver:

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

    def find_teachers(
        self,
        student,
        ability_name,
        cats=None
    ):
        wisdom = FelineWisdom.ensure_state(
            student
        )

        awareness = wisdom[
            "awareness"
        ].get(
            ability_name
        )

        if awareness is None:
            return self._result(
                student=student,
                ability_name=ability_name,
                reason="ability_not_known_to_exist",
                candidates=[],
                teachers=[]
            )

        cats = self._resolve_cats(
            cats
        )

        known_teacher_names = list(
            awareness.get(
                "known_teachers",
                []
            )
        )

        candidates = []
        teachers = []

        for teacher_name in known_teacher_names:
            teacher = self._find_cat(
                cats=cats,
                cat_name=teacher_name
            )

            candidate = {
                "name": teacher_name,
                "cat_found": (
                    teacher is not None
                ),
                "knows_ability": False,
                "methods": []
            }

            if teacher is not None:
                teacher_wisdom = (
                    FelineWisdom.ensure_state(
                        teacher
                    )
                )

                ability = teacher_wisdom[
                    "abilities"
                ].get(
                    ability_name
                )

                if (
                    ability is not None
                    and ability.get(
                        "learned",
                        False
                    )
                ):
                    candidate[
                        "knows_ability"
                    ] = True

                    candidate[
                        "methods"
                    ] = list(
                        ability.get(
                            "methods",
                            {}
                        ).keys()
                    )

                    teachers.append({
                        "cat": teacher,
                        "name": teacher_name,
                        "methods": list(
                            candidate["methods"]
                        )
                    })

            candidates.append(
                candidate
            )

        reason = (
            "teachers_found"
            if teachers
            else "no_available_verified_teacher"
        )

        return self._result(
            student=student,
            ability_name=ability_name,
            reason=reason,
            candidates=candidates,
            teachers=teachers
        )

    def choose_teacher(
        self,
        student,
        ability_name,
        method_name=None,
        cats=None
    ):
        search = self.find_teachers(
            student=student,
            ability_name=ability_name,
            cats=cats
        )

        for teacher in search[
            "teachers"
        ]:
            methods = teacher[
                "methods"
            ]

            if (
                method_name is None
                or method_name in methods
            ):
                event = {
                    "name": (
                        "feline_ability_teacher_chosen"
                    ),
                    "student": student["name"],
                    "ability": ability_name,
                    "requested_method": method_name,
                    "teacher": teacher["name"],
                    "available_methods": list(
                        methods
                    ),
                    "chosen": True
                }

                self._record(
                    event
                )

                return {
                    **event,
                    "teacher_cat": teacher["cat"]
                }

        event = {
            "name": (
                "feline_ability_teacher_not_found"
            ),
            "student": student["name"],
            "ability": ability_name,
            "requested_method": method_name,
            "reason": (
                "no_teacher_knows_requested_method"
                if search["teachers"]
                else search["reason"]
            ),
            "chosen": False
        }

        self._record(
            event
        )

        return event

    def request_lesson(
        self,
        student,
        ability_name,
        ability_resolver,
        method_name=None,
        cats=None
    ):
        choice = self.choose_teacher(
            student=student,
            ability_name=ability_name,
            method_name=method_name,
            cats=cats
        )

        if not choice[
            "chosen"
        ]:
            return {
                "name": (
                    "feline_ability_lesson_request_failed"
                ),
                "student": student["name"],
                "ability": ability_name,
                "requested_method": method_name,
                "reason": choice["reason"],
                "learned": False
            }

        teacher = choice[
            "teacher_cat"
        ]

        selected_method = (
            method_name
            if method_name is not None
            else choice[
                "available_methods"
            ][0]
        )

        lesson = ability_resolver.teach_method(
            teacher=teacher,
            student=student,
            ability_name=ability_name,
            method_name=selected_method
        )

        event = {
            "name": (
                "feline_ability_lesson_requested"
            ),
            "student": student["name"],
            "teacher": teacher["name"],
            "ability": ability_name,
            "method": selected_method,
            "lesson": lesson,
            "learned": lesson.get(
                "learned",
                False
            )
        }

        self._record(
            event
        )

        return event

    def _resolve_cats(
        self,
        cats
    ):
        if cats is not None:
            return list(cats)

        cats_layer = getattr(
            self.universe,
            "cats_layer",
            None
        )

        if cats_layer is None:
            return []

        return list(
            getattr(
                cats_layer,
                "cats",
                []
            )
        )

    def _find_cat(
        self,
        cats,
        cat_name
    ):
        for cat in cats:
            if cat.name == cat_name:
                return cat

        return None

    def _result(
        self,
        student,
        ability_name,
        reason,
        candidates,
        teachers
    ):
        event = {
            "name": (
                "feline_ability_teacher_search"
            ),
            "student": student.get(
                "name"
            ),
            "ability": ability_name,
            "reason": reason,
            "candidates": candidates,
            "teachers": teachers,
            "teacher_count": len(
                teachers
            ),
            "found": bool(
                teachers
            )
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