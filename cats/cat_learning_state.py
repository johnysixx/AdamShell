from dataclasses import (
    dataclass,
    field,
)

from cats.cat_adult_vocalization_state import (
    CatAdultVocalizationState,
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
