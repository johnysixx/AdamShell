from dataclasses import dataclass, field
from types import MappingProxyType

from cats.feline_wisdom import FelineWisdom


class _FrozenFelineTeacherList(tuple):
    pass


def _freeze_feline_teacher_payload(value):
    if isinstance(value, dict):
        return MappingProxyType(
            {
                key: (
                    _freeze_feline_teacher_payload(
                        item
                    )
                )
                for key, item
                in value.items()
            }
        )

    if isinstance(value, list):
        return _FrozenFelineTeacherList(
            _freeze_feline_teacher_payload(
                item
            )
            for item in value
        )

    if isinstance(value, tuple):
        return tuple(
            _freeze_feline_teacher_payload(
                item
            )
            for item in value
        )

    if isinstance(value, set):
        return frozenset(
            _freeze_feline_teacher_payload(
                item
            )
            for item in value
        )

    return value


def _thaw_feline_teacher_payload(value):
    if isinstance(
        value,
        MappingProxyType
    ):
        return {
            key: (
                _thaw_feline_teacher_payload(
                    item
                )
            )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        _FrozenFelineTeacherList
    ):
        return [
            _thaw_feline_teacher_payload(
                item
            )
            for item in value
        ]

    if isinstance(value, tuple):
        return tuple(
            _thaw_feline_teacher_payload(
                item
            )
            for item in value
        )

    if isinstance(value, frozenset):
        return {
            _thaw_feline_teacher_payload(
                item
            )
            for item in value
        }

    return value


@dataclass(
    slots=True,
    frozen=True
)
class FelineTeacherCandidate:

    name: str
    cat_found: bool
    knows_ability: bool
    methods: tuple[str, ...] = ()

    def to_dict(self):
        return {
            "name": self.name,
            "cat_found":
                self.cat_found,
            "knows_ability":
                self.knows_ability,
            "methods": list(
                self.methods
            ),
        }


@dataclass(
    slots=True,
    frozen=True
)
class FelineTeacherMatch:

    cat: object
    name: str
    methods: tuple[str, ...]

    def to_dict(self):
        return {
            "cat": self.cat,
            "name": self.name,
            "methods": list(
                self.methods
            ),
        }


class FelineTeacherHistoryEvent:

    def __deepcopy__(
        self,
        memo
    ):
        return self


@dataclass(
    slots=True,
    frozen=True
)
class FelineAbilityTeacherSearchEvent(
    FelineTeacherHistoryEvent
):

    student: str | None
    ability: str
    reason: str

    candidates: tuple[
        FelineTeacherCandidate,
        ...,
    ]

    teachers: tuple[
        FelineTeacherMatch,
        ...,
    ]

    name: str = field(
        default=(
            "feline_ability_teacher_search"
        ),
        init=False,
    )

    def __post_init__(self):
        if not all(
            isinstance(
                item,
                FelineTeacherCandidate
            )
            for item
            in self.candidates
        ):
            raise TypeError(
                "Feline teacher search "
                "candidates must be "
                "FelineTeacherCandidate objects."
            )

        if not all(
            isinstance(
                item,
                FelineTeacherMatch
            )
            for item
            in self.teachers
        ):
            raise TypeError(
                "Feline teacher search "
                "teachers must be "
                "FelineTeacherMatch objects."
            )

    @property
    def teacher_count(self):
        return len(
            self.teachers
        )

    @property
    def found(self):
        return bool(
            self.teachers
        )

    def to_dict(self):
        return {
            "name": self.name,
            "student": self.student,
            "ability": self.ability,
            "reason": self.reason,
            "candidates": [
                item.to_dict()
                for item
                in self.candidates
            ],
            "teachers": [
                item.to_dict()
                for item
                in self.teachers
            ],
            "teacher_count":
                self.teacher_count,
            "found": self.found,
        }


@dataclass(
    slots=True,
    frozen=True
)
class FelineAbilityTeacherChosenEvent(
    FelineTeacherHistoryEvent
):

    student: str
    ability: str
    requested_method: str | None
    teacher: str
    available_methods: tuple[str, ...]

    name: str = field(
        default=(
            "feline_ability_teacher_chosen"
        ),
        init=False,
    )

    chosen: bool = field(
        default=True,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "student": self.student,
            "ability": self.ability,
            "requested_method":
                self.requested_method,
            "teacher": self.teacher,
            "available_methods": list(
                self.available_methods
            ),
            "chosen": self.chosen,
        }


@dataclass(
    slots=True,
    frozen=True
)
class FelineAbilityTeacherNotFoundEvent(
    FelineTeacherHistoryEvent
):

    student: str
    ability: str
    requested_method: str | None
    reason: str

    name: str = field(
        default=(
            "feline_ability_teacher_not_found"
        ),
        init=False,
    )

    chosen: bool = field(
        default=False,
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "student": self.student,
            "ability": self.ability,
            "requested_method":
                self.requested_method,
            "reason": self.reason,
            "chosen": self.chosen,
        }


@dataclass(
    slots=True,
    frozen=True
)
class FelineAbilityLessonRequestedEvent(
    FelineTeacherHistoryEvent
):

    student: str
    teacher: str
    ability: str
    method: str
    lesson: object
    learned: bool

    name: str = field(
        default=(
            "feline_ability_lesson_requested"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "lesson",
            _freeze_feline_teacher_payload(
                self.lesson
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "student": self.student,
            "teacher": self.teacher,
            "ability": self.ability,
            "method": self.method,
            "lesson": (
                _thaw_feline_teacher_payload(
                    self.lesson
                )
            ),
            "learned": self.learned,
        }


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
        return (
            self._find_teachers_event(
                student=student,
                ability_name=ability_name,
                cats=cats,
            )
            .to_dict()
        )

    def _find_teachers_event(
        self,
        student,
        ability_name,
        cats=None
    ):
        wisdom = (
            FelineWisdom
            .ensure_state(
                student
            )
        )

        awareness = (
            wisdom
            .awareness_record(
                ability_name
            )
        )

        if awareness is None:
            return self._result(
                student=student,
                ability_name=ability_name,
                reason=(
                    "ability_not_known_to_exist"
                ),
                candidates=(),
                teachers=(),
            )

        cats = self._resolve_cats(
            cats
        )

        known_teacher_names = list(
            awareness.known_teachers
        )

        candidates = []
        teachers = []

        for teacher_name in (
            known_teacher_names
        ):
            teacher = self._find_cat(
                cats=cats,
                cat_name=teacher_name
            )

            knows_ability = False
            methods = ()

            if teacher is not None:
                teacher_wisdom = (
                    FelineWisdom
                    .ensure_state(
                        teacher
                    )
                )

                ability = (
                    teacher_wisdom
                    .ability_record(
                        ability_name
                    )
                )

                if (
                    ability is not None
                    and ability.learned
                ):
                    knows_ability = True

                    methods = tuple(
                        ability.method_names()
                    )

                    teachers.append(
                        FelineTeacherMatch(
                            cat=teacher,
                            name=teacher_name,
                            methods=methods,
                        )
                    )

            candidates.append(
                FelineTeacherCandidate(
                    name=teacher_name,
                    cat_found=(
                        teacher is not None
                    ),
                    knows_ability=(
                        knows_ability
                    ),
                    methods=methods,
                )
            )

        reason = (
            "teachers_found"
            if teachers
            else (
                "no_available_verified_teacher"
            )
        )

        return self._result(
            student=student,
            ability_name=ability_name,
            reason=reason,
            candidates=tuple(
                candidates
            ),
            teachers=tuple(
                teachers
            ),
        )

    def choose_teacher(
        self,
        student,
        ability_name,
        method_name=None,
        cats=None
    ):
        event, teacher_cat = (
            self._choose_teacher_event(
                student=student,
                ability_name=ability_name,
                method_name=method_name,
                cats=cats,
            )
        )

        result = event.to_dict()

        if teacher_cat is not None:
            result[
                "teacher_cat"
            ] = teacher_cat

        return result

    def _choose_teacher_event(
        self,
        student,
        ability_name,
        method_name=None,
        cats=None
    ):
        search = (
            self._find_teachers_event(
                student=student,
                ability_name=ability_name,
                cats=cats,
            )
        )

        for teacher in (
            search.teachers
        ):
            methods = teacher.methods

            if (
                method_name is None
                or method_name
                in methods
            ):
                event = (
                    FelineAbilityTeacherChosenEvent(
                        student=student.name,
                        ability=ability_name,
                        requested_method=(
                            method_name
                        ),
                        teacher=(
                            teacher.name
                        ),
                        available_methods=(
                            methods
                        ),
                    )
                )

                self._record(
                    event
                )

                return (
                    event,
                    teacher.cat,
                )

        event = (
            FelineAbilityTeacherNotFoundEvent(
                student=student.name,
                ability=ability_name,
                requested_method=(
                    method_name
                ),
                reason=(
                    (
                        "no_teacher_knows_"
                        "requested_method"
                    )
                    if search.teachers
                    else search.reason
                ),
            )
        )

        self._record(
            event
        )

        return (
            event,
            None,
        )

    def request_lesson(
        self,
        student,
        ability_name,
        ability_resolver,
        method_name=None,
        cats=None
    ):
        choice, teacher = (
            self._choose_teacher_event(
                student=student,
                ability_name=ability_name,
                method_name=method_name,
                cats=cats,
            )
        )

        if not choice.chosen:
            return {
                "name": (
                    "feline_ability_"
                    "lesson_request_failed"
                ),
                "student": student.name,
                "ability": ability_name,
                "requested_method":
                    method_name,
                "reason": choice.reason,
                "learned": False,
            }

        selected_method = (
            method_name
            if method_name is not None
            else (
                choice
                .available_methods[0]
            )
        )

        lesson = (
            ability_resolver
            .teach_method(
                teacher=teacher,
                student=student,
                ability_name=(
                    ability_name
                ),
                method_name=(
                    selected_method
                ),
            )
        )

        event = (
            FelineAbilityLessonRequestedEvent(
                student=student.name,
                teacher=teacher.name,
                ability=ability_name,
                method=selected_method,
                lesson=lesson,
                learned=lesson.get(
                    "learned",
                    False
                ),
            )
        )

        self._record(
            event
        )

        return event.to_dict()

    def _resolve_cats(
        self,
        cats
    ):
        if cats is not None:
            return list(
                cats
            )

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
        event = (
            FelineAbilityTeacherSearchEvent(
                student=getattr(
                    student,
                    "name",
                    None
                ),
                ability=ability_name,
                reason=reason,
                candidates=tuple(
                    candidates
                ),
                teachers=tuple(
                    teachers
                ),
            )
        )

        self._record(
            event
        )

        return event

    def _record(
        self,
        event
    ):
        if not isinstance(
            event,
            FelineTeacherHistoryEvent
        ):
            raise TypeError(
                "Feline teacher history "
                "requires a typed feline "
                "teacher event object."
            )

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
                event.to_dict()
            )

        return event
