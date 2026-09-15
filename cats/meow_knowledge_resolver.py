from cats.feline_wisdom import FelineWisdom
from cats.cat_learning_state import CatLearningState

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
            event = {'name': 'meow_knowledge_transmission_denied', 'mother': getattr(mother, 'name', None), 'kitten': getattr(kitten, 'name', None), 'day': current_day, 'reason': readiness['reason'], 'missing_experiences': readiness.get('missing_experiences', []), 'transmitted': False}
            self.history.append(event)
            return event
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
        learning.lessons.append({'name': 'mother_spoke_meow' if teacher_role['role'] == 'biological_mother' else 'dice_cat_spoke_meow', 'teacher': mother.name, 'student': kitten.name, 'day': current_day, 'knowledge': list(meow.contains)})
        learning.complete = all(
            skill.learned
            for skill in learning.skills.values()
        )
        if learning.complete:
            learning.teaching_required = False
        event = {'name': 'meow_knowledge_transmitted', 'mother': mother.name, 'kitten': kitten.name, 'day': current_day, 'knowledge': list(meow.contains), 'adult_meowing_learned': learning.adult_meowing_learned, 'human_communication_learned': learning.human_communication_learned, 'learning_complete': learning.complete, 'teacher_role': teacher_role['role'], 'transmission_source': transmission_source, 'awareness_transferred': wisdom_result['transferred_count'], 'ability_methods_transferred': 0, 'transmitted': True}
        self.history.append(event)
        quantum_events = getattr(self.universe, 'quantum_events', None)
        if quantum_events is not None:
            quantum_events.append(event)
        return event

    def _resolve_teacher_role(self, teacher, kitten):
        teacher_name = getattr(teacher, 'name', None)
        parents = getattr(kitten, 'parents', None)
        if parents is not None:
            mother_name = parents.get('mother')
        else:
            mother_name = getattr(
                getattr(kitten, 'learning', None),
                'teacher_mother',
                None,
            )
        if mother_name is not None and teacher_name == mother_name:
            return {'allowed': True, 'reason': 'biological_mother_available', 'role': 'biological_mother'}
        teacher_wisdom = FelineWisdom.ensure_state(teacher)
        teaching_ability = teacher_wisdom['abilities'].get('teach_other_cats')
        can_teach_other_cats = bool(teaching_ability and teaching_ability.get('learned', False))
        if can_teach_other_cats:
            return {'allowed': True, 'reason': 'qualified_feline_teacher', 'role': 'dice_cat_teacher' if getattr(teacher, 'origin', None) == 'dice_manifestation' else 'qualified_cat_teacher'}
        return {'allowed': False, 'reason': 'teacher_has_not_learned_to_teach', 'role': None}

    def _transmit_feline_awareness(self, teacher, kitten, current_day):
        teacher_wisdom = FelineWisdom.ensure_state(teacher)
        kitten_wisdom = FelineWisdom.ensure_state(kitten)
        transferred = []
        for knowledge_name, knowledge in teacher_wisdom['awareness'].items():
            domain = knowledge.get('domain')
            if domain not in FelineWisdom.MEOW_ALLOWED_DOMAINS:
                continue
            copied = {'name': knowledge_name, 'domain': domain, 'known_to_exist': True, 'description': knowledge.get('description'), 'known_teachers': list(knowledge.get('known_teachers', [])), 'transfer_mode': 'awareness_only', 'received_from': teacher.name, 'received_on_day': current_day}
            kitten_wisdom['awareness'][knowledge_name] = copied
            transferred.append(copied)
        event = {'name': 'meow_feline_awareness_transmitted', 'teacher': teacher.name, 'kitten': kitten.name, 'day': current_day, 'transferred': transferred, 'transferred_count': len(transferred), 'ability_methods_transferred': 0}
        teacher_wisdom['transmission_history'].append(event)
        kitten_wisdom['transmission_history'].append(event)
        return event

    def _complete_skill(self, kitten, skill_name, teacher_name, current_day):
        skill = kitten.learning.skills[skill_name]
        skill.learned = True
        skill.progress = 1.0
        skill.teacher = teacher_name
        skill.learned_on_day = current_day
