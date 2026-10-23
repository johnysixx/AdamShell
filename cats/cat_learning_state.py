from copy import deepcopy
from dataclasses import (
    dataclass,
    field,
    fields,
    is_dataclass,
)
from enum import Enum

from cats.cat_adult_vocalization_state import (
    CatAdultVocalizationState,
)


def _learning_snapshot_value(
    value,
):
    serializer = getattr(
        value,
        "to_dict",
        None,
    )

    if callable(
        serializer
    ):
        return deepcopy(
            serializer()
        )

    if isinstance(
        value,
        Enum,
    ):
        return value.value

    if is_dataclass(
        value
    ):
        return {
            item.name: (
                _learning_snapshot_value(
                    getattr(
                        value,
                        item.name,
                    )
                )
            )
            for item
            in fields(value)
        }

    if isinstance(
        value,
        dict,
    ):
        return {
            key: (
                _learning_snapshot_value(
                    item
                )
            )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
            frozenset,
        ),
    ):
        return [
            _learning_snapshot_value(
                item
            )
            for item
            in value
        ]

    return deepcopy(
        value
    )


@dataclass(slots=True)
class CatSkillState:

    name: str
    learned: bool = False
    progress: float = 0.0
    teacher: str | None = None
    learned_on_day: int | None = None
    vocalizations: CatAdultVocalizationState | None = None

    def __post_init__(
        self,
    ):
        self.name = str(
            self.name
        )

        if not self.name:
            raise ValueError(
                "Cat skill requires name."
            )

@dataclass(slots=True)
class CatSkillRegistry:

    _skills: list = field(
        default_factory=list
    )

    @property
    def is_empty(
        self,
    ):
        return not self._skills

    @property
    def count(
        self,
    ):
        return len(
            self._skills
        )

    def store(
        self,
        skill,
    ):
        if not isinstance(
            skill,
            CatSkillState,
        ):
            raise TypeError(
                "Cat skill registry requires "
                "CatSkillState."
            )

        for index, current in enumerate(
            self.records()
        ):
            if current.name == skill.name:
                self._skills[
                    index
                ] = skill

                return skill

        self._skills.append(
            skill
        )

        return skill

    def record(
        self,
        name,
    ):
        name = str(
            name
        )

        for skill in self.records():
            if skill.name == name:
                return skill

        return None

    def records(
        self,
    ):
        for skill in self._skills:
            if not isinstance(
                skill,
                CatSkillState,
            ):
                raise TypeError(
                    "Cat skill registry contains "
                    "invalid runtime state."
                )

        return tuple(
            self._skills
        )

    def names(
        self,
    ):
        return tuple(
            skill.name
            for skill
            in self.records()
        )


@dataclass(slots=True)
class CatMeowKnowledgeState:

    learned: bool = False
    understood: bool = False
    can_speak: bool = False
    teacher: str | None = None
    source: str | None = None
    learned_on_day: int | None = None
    contains: list = field(default_factory=list)

@dataclass(slots=True)
class CatFamilyKnowledgeState:

    parental_lessons: int = 0

@dataclass(slots=True)
class CatLearningState:

    teaching_required: bool = False
    teaching_deadline_days: int | None = None
    teacher_mother: str | None = None
    hunting_teacher_father: str | None = None
    kitten_meowing_instinctive: bool = True
    adult_meowing_learned: bool = False
    human_communication_learned: bool = False
    meow_knowledge: CatMeowKnowledgeState = field(
        default_factory=CatMeowKnowledgeState
    )
    skills: CatSkillRegistry = field(
        default_factory=CatSkillRegistry
    )
    lessons: list = field(default_factory=list)
    family_knowledge: CatFamilyKnowledgeState = field(
        default_factory=CatFamilyKnowledgeState
    )
    complete: bool = False

    def __post_init__(
        self,
    ):
        if not isinstance(
            self.skills,
            CatSkillRegistry,
        ):
            raise TypeError(
                "Cat learning skills must use "
                "CatSkillRegistry."
            )

    def to_dict(self):
        return {
            "teaching_required":
                self.teaching_required,

            "teaching_deadline_days": (
                self.teaching_deadline_days
            ),

            "teacher_mother":
                self.teacher_mother,

            "hunting_teacher_father": (
                self.hunting_teacher_father
            ),

            "kitten_meowing_instinctive": (
                self.kitten_meowing_instinctive
            ),

            "adult_meowing_learned": (
                self.adult_meowing_learned
            ),

            "human_communication_learned": (
                self.human_communication_learned
            ),

            "meow_knowledge": {
                "learned":
                    self.meow_knowledge.learned,

                "understood":
                    self.meow_knowledge.understood,

                "can_speak":
                    self.meow_knowledge.can_speak,

                "teacher":
                    self.meow_knowledge.teacher,

                "source":
                    self.meow_knowledge.source,

                "learned_on_day": (
                    self.meow_knowledge
                    .learned_on_day
                ),

                "contains": list(
                    self.meow_knowledge.contains
                ),
            },

            "skills": {
                skill.name: {
                    "learned":
                        skill.learned,

                    "progress":
                        skill.progress,

                    "teacher":
                        skill.teacher,

                    "learned_on_day": (
                        skill.learned_on_day
                    ),

                    **(
                        {
                            "vocalizations":
                                _learning_snapshot_value(
                                    skill.vocalizations
                                )
                        }
                        if (
                            skill.vocalizations
                            is not None
                        )
                        else {}
                    ),
                }
                for skill
                in self.skills.records()
            },

            "lessons": [
                _learning_snapshot_value(
                    lesson
                )
                for lesson
                in self.lessons
            ],

            "family_knowledge": {
                "parental_lessons": (
                    self.family_knowledge
                    .parental_lessons
                ),
            },

            "complete":
                self.complete,
        }

