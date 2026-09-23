from dataclasses import dataclass, field

from cats.feline_wisdom import FelineWisdom
from cats.cat_learning_state import CatLearningState
from cats.cat_parentage_state import (
    CatParentageState
)

@dataclass(slots=True, frozen=True)
class MeowKnowledgeLesson:
    name: str
    teacher: str
    student: str
    day: int
    knowledge: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(
            self,
            "knowledge",
            tuple(self.knowledge),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "teacher": self.teacher,
            "student": self.student,
            "day": self.day,
            "knowledge": list(self.knowledge),
        }


@dataclass(slots=True, frozen=True)
class MeowKnowledgeTransmissionDeniedEvent:
    mother: str | None
    kitten: str | None
    day: int
    reason: str
    missing_experiences: tuple[str, ...]
    name: str = field(
        default="meow_knowledge_transmission_denied",
        init=False,
    )
    transmitted: bool = field(
        default=False,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "missing_experiences",
            tuple(self.missing_experiences),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "mother": self.mother,
            "kitten": self.kitten,
            "day": self.day,
            "reason": self.reason,
            "missing_experiences": list(
                self.missing_experiences
            ),
            "transmitted": self.transmitted,
        }


@dataclass(slots=True, frozen=True)
class MeowKnowledgeTransmittedEvent:
    mother: str
    kitten: str
    day: int
    knowledge: tuple[str, ...]
    adult_meowing_learned: bool
    human_communication_learned: bool
    learning_complete: bool
    teacher_role: str
    transmission_source: str
    awareness_transferred: int
    ability_methods_transferred: int = 0
    name: str = field(
        default="meow_knowledge_transmitted",
        init=False,
    )
    transmitted: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "knowledge",
            tuple(self.knowledge),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "mother": self.mother,
            "kitten": self.kitten,
            "day": self.day,
            "knowledge": list(self.knowledge),
            "adult_meowing_learned": (
                self.adult_meowing_learned
            ),
            "human_communication_learned": (
                self.human_communication_learned
            ),
            "learning_complete": self.learning_complete,
            "teacher_role": self.teacher_role,
            "transmission_source": (
                self.transmission_source
            ),
            "awareness_transferred": (
                self.awareness_transferred
            ),
            "ability_methods_transferred": (
                self.ability_methods_transferred
            ),
            "transmitted": self.transmitted,
        }


class MeowKnowledgeResolver:
    REQUIRED_EXPERIENCES = ('socialization', 'litter_box', 'box_travel', 'cat_door_travel', 'hunting', 'adult_meowing', 'human_communication')

    def __init__(self, universe):
        self.universe = universe
        self.history = []

    def can_receive_meow(self, kitten, mother):
        kitten_learning = getattr(kitten, 'learning', None)
        mother_learning = getattr(mother, 'learning', None)
        kitten_meow = getattr(
            kitten_learning,
            'meow_knowledge',
            None,
        )
        mother_meow = getattr(
            mother_learning,
            'meow_knowledge',
            None,
        )
        if getattr(kitten, 'type', None) != 'cat':
            return {'allowed': False, 'reason': 'receiver_is_not_cat'}
        if getattr(mother, 'type', None) != 'cat':
            return {'allowed': False, 'reason': 'teacher_is_not_cat'}
        teacher_role = self._resolve_teacher_role(teacher=mother, kitten=kitten)
        if not teacher_role['allowed']:
            return teacher_role
        if kitten_meow is None:
            return {'allowed': False, 'reason': 'learning_state_unavailable'}
        if mother_meow is None:
            return {'allowed': False, 'reason': 'mother_does_not_know_meow'}
        if kitten_meow.learned:
            return {'allowed': False, 'reason': 'meow_already_known'}
        if not mother_meow.learned:
            return {'allowed': False, 'reason': 'mother_does_not_know_meow'}
        if not mother_meow.can_speak:
            return {'allowed': False, 'reason': 'mother_cannot_speak_meow'}
        skills = (
            kitten_learning.skills
            if isinstance(kitten_learning, CatLearningState)
            else {}
        )
        missing_experiences = [
            skill_name
            for skill_name in self.REQUIRED_EXPERIENCES
            if (
                skills.get(skill_name) is None
                or not skills[skill_name].learned
            )
        ]
        if missing_experiences:
            return {'allowed': False, 'reason': 'required_experiences_missing', 'missing_experiences': missing_experiences}
        return {'allowed': True, 'reason': 'ready_for_meow', 'missing_experiences': []}

    def transmit(self, mother, kitten, current_day):
        readiness = self.can_receive_meow(kitten, mother)
        if not readiness['allowed']:
            event = MeowKnowledgeTransmissionDeniedEvent(
                mother=getattr(
                    mother,
                    'name',
                    None,
                ),
                kitten=getattr(
                    kitten,
                    'name',
                    None,
                ),
                day=current_day,
                reason=readiness['reason'],
                missing_experiences=tuple(
                    readiness.get(
                        'missing_experiences',
                        [],
                    )
                ),
            )

            self.history.append(
                event
            )

            return event.to_dict()
        learning = kitten.learning
        meow = learning.meow_knowledge
        teacher_role = self._resolve_teacher_role(teacher=mother, kitten=kitten)
        if teacher_role['role'] == 'biological_mother':
            transmission_source = 'maternal_transmission'
        elif teacher_role['role'] == 'dice_cat_teacher':
            transmission_source = 'qualified_dice_cat_transmission'
        else:
            transmission_source = 'qualified_cat_transmission'
        meow.learned = True
        meow.understood = True
        meow.can_speak = True
        meow.teacher = mother.name
        meow.source = transmission_source
        meow.learned_on_day = current_day
        wisdom_result = self._transmit_feline_awareness(teacher=mother, kitten=kitten, current_day=current_day)
        lesson = MeowKnowledgeLesson(
            name=(
                'mother_spoke_meow'
                if teacher_role['role']
                == 'biological_mother'
                else 'dice_cat_spoke_meow'
            ),
            teacher=mother.name,
            student=kitten.name,
            day=current_day,
            knowledge=tuple(
                meow.contains
            ),
        )

        learning.lessons.append(
            lesson
        )
        learning.complete = all(
            skill.learned
            for skill in learning.skills.values()
        )
        if learning.complete:
            learning.teaching_required = False
        event = MeowKnowledgeTransmittedEvent(
            mother=mother.name,
            kitten=kitten.name,
            day=current_day,
            knowledge=tuple(
                meow.contains
            ),
            adult_meowing_learned=(
                learning.adult_meowing_learned
            ),
            human_communication_learned=(
                learning.human_communication_learned
            ),
            learning_complete=learning.complete,
            teacher_role=teacher_role['role'],
            transmission_source=(
                transmission_source
            ),
            awareness_transferred=(
                wisdom_result[
                    'transferred_count'
                ]
            ),
        )

        self.history.append(
            event
        )

        snapshot = event.to_dict()

        quantum_events = getattr(
            self.universe,
            'quantum_events',
            None,
        )

        if quantum_events is not None:
            quantum_events.append(
                event.to_dict()
            )

        return snapshot

    def _resolve_teacher_role(self, teacher, kitten):
        teacher_name = getattr(teacher, 'name', None)
        parentage = (
            CatParentageState
            .require_from_cat(kitten)
        )

        mother_name = (
            parentage.mother
        )
        if mother_name is not None and teacher_name == mother_name:
            return {'allowed': True, 'reason': 'biological_mother_available', 'role': 'biological_mother'}
        teacher_wisdom = FelineWisdom.ensure_state(teacher)
        teaching_ability = (
            teacher_wisdom
            .ability_record(
                'teach_other_cats'
            )
        )

        can_teach_other_cats = bool(
            teaching_ability is not None
            and teaching_ability.learned
        )
        if can_teach_other_cats:
            return {'allowed': True, 'reason': 'qualified_feline_teacher', 'role': 'dice_cat_teacher' if getattr(teacher, 'origin', None) == 'dice_manifestation' else 'qualified_cat_teacher'}
        return {'allowed': False, 'reason': 'teacher_has_not_learned_to_teach', 'role': None}

    def _transmit_feline_awareness(self, teacher, kitten, current_day):
        teacher_wisdom = FelineWisdom.ensure_state(teacher)
        kitten_wisdom = FelineWisdom.ensure_state(kitten)
        transferred = []
        for knowledge_name, knowledge in teacher_wisdom.awareness_items():
            domain = knowledge.domain
            if domain not in FelineWisdom.MEOW_ALLOWED_DOMAINS:
                continue
            copied = knowledge.copy_for_transfer(
                received_from=teacher.name,
                received_on_day=current_day,
            )
            kitten_wisdom.store_awareness(copied)
            transferred.append(copied)
        event = {'name': 'meow_feline_awareness_transmitted', 'teacher': teacher.name, 'kitten': kitten.name, 'day': current_day, 'transferred': transferred, 'transferred_count': len(transferred), 'ability_methods_transferred': 0}
        teacher_wisdom.transmission_history.append(event)
        kitten_wisdom.transmission_history.append(event)
        return event

    def _complete_skill(self, kitten, skill_name, teacher_name, current_day):
        skill = kitten.learning.skills[skill_name]
        skill.learned = True
        skill.progress = 1.0
        skill.teacher = teacher_name
        skill.learned_on_day = current_day
