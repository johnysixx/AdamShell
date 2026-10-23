from copy import deepcopy
from dataclasses import dataclass, field
from cats.cat_personality_state import (
    CatPersonalityExperienceAppliedResult,
    CatPersonalityTraitAdjustedEvent,
)

def _personality_trait_event_snapshot(
    event,
):
    if not isinstance(
        event,
        CatPersonalityTraitAdjustedEvent,
    ):
        raise TypeError(
            "Personality snapshot event must be "
            "CatPersonalityTraitAdjustedEvent."
        )

    return {
        "name": event.name,
        "cat": event.cat,
        "trait": event.trait,
        "source": event.source,
        "day": event.day,
        "previous": event.previous,
        "requested_change": (
            event.requested_change
        ),
        "applied_change": (
            event.applied_change
        ),
        "value": event.value,
        "metadata": deepcopy(
            dict(
                event.metadata
            )
        ),
    }


def _personality_experience_snapshot(
    result,
):
    if not isinstance(
        result,
        CatPersonalityExperienceAppliedResult,
    ):
        raise TypeError(
            "Personality snapshot result must be "
            "CatPersonalityExperienceAppliedResult."
        )

    return {
        "name": result.name,
        "cat": result.cat,
        "source": result.source,
        "day": result.day,
        "changes": deepcopy(
            dict(
                result.changes
            )
        ),
        "events": [
            _personality_trait_event_snapshot(
                event
            )
            for event in result.events
        ],
        "applied": result.applied,
    }


from cats.feline_ability_state import (
    FelineAbilityState,
)
from cats.feline_ability_method_state import (
    FelineAbilityMethodConstraints,
    FelineAbilityMethodState,
)
from cats.feline_awareness_state import (
    FelineAwarenessState,
)
from cats.feline_wisdom_registry import (
    FelineAbilityRegistry,
    FelineAwarenessRegistry,
)


def _ability_method_constraints_snapshot(
    constraints,
):
    if not isinstance(
        constraints,
        FelineAbilityMethodConstraints,
    ):
        raise TypeError(
            "Feline ability constraint snapshot "
            "requires "
            "FelineAbilityMethodConstraints."
        )

    snapshot = {}

    for field_name in (
        "requires_unlocked",
        "opens_toward_cat",
        "opens_away_from_cat",
        "can_close",
        "can_teach_meow",
        "can_teach_owned_abilities",
        "can_teach_to_own_kittens",
        "can_create_foreign_teachers",
        "can_teach_teach_other_cats",
        "can_teach_teach_teaching",
    ):
        value = getattr(
            constraints,
            field_name,
        )

        if value is not None:
            snapshot[
                field_name
            ] = value

    return snapshot


@dataclass(slots=True, frozen=True)
class MeowFelineAwarenessTransmissionEvent:
    teacher: str
    kitten: str
    day: int
    transferred: tuple[
        FelineAwarenessState,
        ...
    ]
    name: str = field(
        default=(
            "meow_feline_awareness_transmitted"
        ),
        init=False,
    )
    ability_methods_transferred: int = field(
        default=0,
        init=False,
    )

    def __post_init__(self):
        transferred = tuple(
            self.transferred
        )

        if not all(
            isinstance(
                awareness,
                FelineAwarenessState,
            )
            for awareness in transferred
        ):
            raise TypeError(
                "Transferred feline awareness "
                "must contain "
                "FelineAwarenessState objects."
            )

        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )
        object.__setattr__(
            self,
            "kitten",
            str(self.kitten),
        )
        object.__setattr__(
            self,
            "day",
            int(self.day),
        )
        object.__setattr__(
            self,
            "transferred",
            transferred,
        )

    @property
    def transferred_count(self):
        return len(
            self.transferred
        )

@dataclass(slots=True, frozen=True)
class FelineAbilityAwarenessTransmissionDeniedResult:
    teacher: str
    student: str
    reason: str

    name: str = field(
        default=(
            "meow_awareness_transmission_denied"
        ),
        init=False,
    )

    learned: bool = field(
        default=False,
        init=False,
    )

    transmitted: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )
        object.__setattr__(
            self,
            "student",
            str(self.student),
        )
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "student": self.student,
            "reason": self.reason,
            "learned": self.learned,
            "transmitted": self.transmitted,
        }


@dataclass(slots=True, frozen=True)
class FelineAbilityAwarenessTransmissionEvent:
    teacher: str
    student: str
    transferred: tuple[
        FelineAwarenessState,
        ...
    ]
    name: str = field(
        default=(
            "meow_ability_awareness_transmitted"
        ),
        init=False,
    )
    methods_transferred: int = field(
        default=0,
        init=False,
    )
    transmitted: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        transferred = tuple(
            self.transferred
        )

        if not all(
            isinstance(
                awareness,
                FelineAwarenessState,
            )
            for awareness in transferred
        ):
            raise TypeError(
                "Transferred feline awareness "
                "must contain "
                "FelineAwarenessState objects."
            )

        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )
        object.__setattr__(
            self,
            "student",
            str(self.student),
        )
        object.__setattr__(
            self,
            "transferred",
            transferred,
        )

    @property
    def transferred_count(self):
        return len(
            self.transferred
        )

    def to_dict(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "student": self.student,
            "transferred": list(
                self.transferred
            ),
            "transferred_count": (
                self.transferred_count
            ),
            "methods_transferred": (
                self.methods_transferred
            ),
            "transmitted": self.transmitted,
        }


@dataclass(slots=True, frozen=True)
class FelineHumanDoorCapabilityResult:
    cat: str
    action: str
    allowed: bool
    reason: str
    usable_methods: tuple[str, ...] = ()

    name: str = field(
        default=(
            "feline_human_door_capability"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        action = str(
            self.action
        )

        if action not in (
            "open",
            "close",
        ):
            raise ValueError(
                "Feline human door action must "
                "be 'open' or 'close'."
            )

        object.__setattr__(
            self,
            "action",
            action,
        )

        object.__setattr__(
            self,
            "allowed",
            bool(
                self.allowed
            ),
        )

        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

        object.__setattr__(
            self,
            "usable_methods",
            tuple(
                str(method)
                for method
                in self.usable_methods
            ),
        )


@dataclass(slots=True, frozen=True)
class FelineAbilityMethodRegistrationResult:
    name: str
    cat: str
    ability: str
    method: FelineAbilityMethodState

    registered: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "name",
            str(self.name),
        )
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )
        object.__setattr__(
            self,
            "ability",
            str(self.ability),
        )

        if not isinstance(
            self.method,
            FelineAbilityMethodState,
        ):
            raise TypeError(
                "Registered feline ability method "
                "must be FelineAbilityMethodState."
            )


@dataclass(slots=True, frozen=True)
class FelineTeachingAbilitiesRegistrationResult:
    cat: str
    teach_other_cats: FelineAbilityMethodState
    teach_teaching: FelineAbilityMethodState

    name: str = field(
        default=(
            "garfield_teaching_"
            "abilities_registered"
        ),
        init=False,
    )

    registered: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )

        for method in (
            self.teach_other_cats,
            self.teach_teaching,
        ):
            if not isinstance(
                method,
                FelineAbilityMethodState,
            ):
                raise TypeError(
                    "Registered feline teaching "
                    "ability must contain "
                    "FelineAbilityMethodState objects."
                )

    def to_dict(self):
        return {
            "name": self.name,
            "cat": self.cat,
            "teach_other_cats": {
                "name":
                    self.teach_other_cats.name,
                "teacher":
                    self.teach_other_cats.teacher,
                "constraints": (
                    _ability_method_constraints_snapshot(
                        self.teach_other_cats
                        .constraints
                    )
                ),
            },
            "teach_teaching": {
                "name":
                    self.teach_teaching.name,
                "teacher":
                    self.teach_teaching.teacher,
                "constraints": (
                    _ability_method_constraints_snapshot(
                        self.teach_teaching
                        .constraints
                    )
                ),
            },
            "registered":
                self.registered,
        }


@dataclass(slots=True, frozen=True)
class FelineTeachingPermissionResult:
    teacher: str
    student: str
    ability: str
    allowed: bool
    reason: str
    creates_cronenberg: bool = False

    name: str = field(
        default="feline_teaching_permission",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )

        object.__setattr__(
            self,
            "student",
            str(self.student),
        )

        object.__setattr__(
            self,
            "ability",
            str(self.ability),
        )

        object.__setattr__(
            self,
            "allowed",
            bool(self.allowed),
        )

        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

        object.__setattr__(
            self,
            "creates_cronenberg",
            bool(
                self.creates_cronenberg
            ),
        )


@dataclass(slots=True, frozen=True)
class FelineAbilityLessonDeniedResult:
    teacher: str
    student: str
    reason: str

    name: str = field(
        default="feline_ability_lesson_denied",
        init=False,
    )

    learned: bool = field(
        default=False,
        init=False,
    )

    transmitted: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )
        object.__setattr__(
            self,
            "student",
            str(self.student),
        )
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "student": self.student,
            "reason": self.reason,
            "learned": self.learned,
            "transmitted": self.transmitted,
        }


@dataclass(slots=True, frozen=True)
class FelineAbilityTeachingCronenbergResult:
    teacher: str
    student: str
    attempted_ability: str
    reason: str
    cronenberg_id: object

    name: str = field(
        default=(
            "forbidden_teaching_"
            "created_cronenberg"
        ),
        init=False,
    )

    cronenberg_created: bool = field(
        default=True,
        init=False,
    )

    learned: bool = field(
        default=False,
        init=False,
    )

    transmitted: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )
        object.__setattr__(
            self,
            "student",
            str(self.student),
        )
        object.__setattr__(
            self,
            "attempted_ability",
            str(self.attempted_ability),
        )
        object.__setattr__(
            self,
            "reason",
            str(self.reason),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "student": self.student,
            "attempted_ability":
                self.attempted_ability,
            "reason": self.reason,
            "cronenberg_id":
                self.cronenberg_id,
            "cronenberg_created":
                self.cronenberg_created,
            "learned": self.learned,
            "transmitted": self.transmitted,
        }


@dataclass(slots=True, frozen=True)
class FelineAbilityMethodLearnedEvent:
    teacher: str
    student: str
    ability: str
    method: str
    constraints: object
    teacher_personality: CatPersonalityExperienceAppliedResult
    student_personality: CatPersonalityExperienceAppliedResult

    name: str = field(
        default="feline_ability_method_learned",
        init=False,
    )

    learned: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "teacher",
            str(self.teacher),
        )
        object.__setattr__(
            self,
            "student",
            str(self.student),
        )
        object.__setattr__(
            self,
            "ability",
            str(self.ability),
        )
        object.__setattr__(
            self,
            "method",
            str(self.method),
        )

        if not isinstance(
            self.constraints,
            FelineAbilityMethodConstraints,
        ):
            raise TypeError(
                "Learned feline ability constraints "
                "must use "
                "FelineAbilityMethodConstraints."
            )

        if not isinstance(
            self.teacher_personality,
            CatPersonalityExperienceAppliedResult,
        ):
            raise TypeError(
                "Teacher personality result must "
                "be CatPersonalityExperienceAppliedResult."
            )

        if not isinstance(
            self.student_personality,
            CatPersonalityExperienceAppliedResult,
        ):
            raise TypeError(
                "Student personality result must "
                "be CatPersonalityExperienceAppliedResult."
            )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "student": self.student,
            "ability": self.ability,
            "method": self.method,
            "constraints": (
                _ability_method_constraints_snapshot(
                    self.constraints
                )
            ),
            "teacher_personality": (
                _personality_experience_snapshot(
                    self.teacher_personality
                )
            ),
            "student_personality": (
                _personality_experience_snapshot(
                    self.student_personality
                )
            ),
            "learned": self.learned,
        }


@dataclass(slots=True)
class FelineWisdomState:
    can_transmit_meow: bool = False
    awareness: FelineAwarenessRegistry = field(
        default_factory=(
            FelineAwarenessRegistry
        )
    )
    abilities: FelineAbilityRegistry = field(
        default_factory=(
            FelineAbilityRegistry
        )
    )
    transmission_history: list = field(
        default_factory=list
    )
    lesson_history: list = field(
        default_factory=list
    )

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.awareness,
            FelineAwarenessRegistry,
        ):
            raise TypeError(
                "Feline wisdom awareness must use "
                "FelineAwarenessRegistry."
            )

        if not isinstance(
            self.abilities,
            FelineAbilityRegistry,
        ):
            raise TypeError(
                "Feline wisdom abilities must use "
                "FelineAbilityRegistry."
            )

    def record_transmission(
        self,
        event,
    ):
        if not isinstance(
            event,
            (
                MeowFelineAwarenessTransmissionEvent,
                FelineAbilityAwarenessTransmissionEvent,
            ),
        ):
            raise TypeError(
                "Feline wisdom transmission "
                "history requires a feline "
                "awareness transmission "
                "event object."
            )

        self.transmission_history.append(
            event
        )

        return event

    def record_lesson(
        self,
        event,
    ):
        if not isinstance(
            event,
            FelineAbilityMethodLearnedEvent,
        ):
            raise TypeError(
                "Feline wisdom lesson history "
                "requires a "
                "FelineAbilityMethodLearnedEvent object."
            )

        self.lesson_history.append(
            event
        )

        return event

    def set_can_transmit_meow(
        self,
        enabled,
    ):
        self.can_transmit_meow = bool(
            enabled
        )

        return self

    def store_awareness(
        self,
        awareness,
    ):
        if not isinstance(
            awareness,
            FelineAwarenessState,
        ):
            raise TypeError(
                "Feline awareness record must "
                "be FelineAwarenessState."
            )

        return self.awareness.store(
            awareness
        )

    def awareness_record(
        self,
        knowledge_name,
    ):
        return self.awareness.record(
            knowledge_name
        )

    def awareness_records(
        self,
    ):
        return self.awareness.records()

    def store_ability(
        self,
        ability_name,
        ability,
    ):
        if not isinstance(
            ability,
            FelineAbilityState,
        ):
            raise TypeError(
                "Feline ability record must "
                "be FelineAbilityState."
            )

        return self.abilities.store(
            ability_name,
            ability,
        )

    def remove_ability(
        self,
        ability_name,
    ):
        return self.abilities.remove(
            ability_name
        )

    def ability_record(
        self,
        ability_name,
    ):
        return self.abilities.record(
            ability_name
        )

    def ensure_ability(
        self,
        ability_name,
    ):
        ability = self.ability_record(
            ability_name
        )

        if ability is None:
            ability = FelineAbilityState()

            self.store_ability(
                ability_name,
                ability,
            )

        return ability

    def ability_records(
        self,
    ):
        return self.abilities.records()
