from copy import deepcopy
from dataclasses import dataclass, field

from cats.cat_adult_vocalization_state import (
    CatAdultVocalizationState,
)


@dataclass(slots=True)
class CatSkillState:

    learned: bool = False
    progress: float = 0.0
    teacher: str | None = None
    learned_on_day: int | None = None
    vocalizations: CatAdultVocalizationState | None = None

    def to_dict(self):
        state = {
            "learned": self.learned,
            "progress": self.progress,
            "teacher": self.teacher,
            "learned_on_day": self.learned_on_day,
        }

        if self.vocalizations is not None:
            state["vocalizations"] = (
                self.vocalizations.to_dict()
            )

        return state


@dataclass(slots=True)
class CatMeowKnowledgeState:

    learned: bool = False
    understood: bool = False
    can_speak: bool = False
    teacher: str | None = None
    source: str | None = None
    learned_on_day: int | None = None
    contains: list = field(default_factory=list)

    def to_dict(self):
        return {
            "learned": self.learned,
            "understood": self.understood,
            "can_speak": self.can_speak,
            "teacher": self.teacher,
            "source": self.source,
            "learned_on_day": self.learned_on_day,
            "contains": list(self.contains),
        }


@dataclass(slots=True)
class CatFamilyKnowledgeState:

    parental_lessons: int = 0

    def to_dict(self):
        return {
            "parental_lessons": self.parental_lessons,
        }


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
    skills: dict = field(default_factory=dict)
    lessons: list = field(default_factory=list)
    family_knowledge: CatFamilyKnowledgeState = field(
        default_factory=CatFamilyKnowledgeState
    )
    complete: bool = False

    def to_dict(self):
        return {
            "teaching_required": self.teaching_required,
            "teaching_deadline_days": (
                self.teaching_deadline_days
            ),
            "teacher_mother": self.teacher_mother,
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
            "meow_knowledge": self.meow_knowledge.to_dict(),
            "skills": {
                name: skill.to_dict()
                for name, skill in self.skills.items()
            },
            "lessons": [
                (
                    deepcopy(
                        lesson.to_dict()
                    )
                    if callable(
                        getattr(
                            lesson,
                            "to_dict",
                            None,
                        )
                    )
                    else deepcopy(
                        lesson
                    )
                )
                for lesson in self.lessons
            ],
            "family_knowledge": (
                self.family_knowledge.to_dict()
            ),
            "complete": self.complete,
        }
