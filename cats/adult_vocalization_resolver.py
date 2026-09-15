from cats.cat_learning import CatLearning
from cats.cat_learning_state import CatLearningState

class AdultVocalizationResolver:

    def __init__(self, universe):
        self.universe = universe
        self.history = []

    def teach(self, teacher, kitten, vocalization, current_day):
        if vocalization not in CatLearning.ADULT_VOCALIZATIONS:
            raise ValueError('Unknown adult feline vocalization.')
        teacher_learning = getattr(teacher, 'learning', None)
        kitten_learning = getattr(kitten, 'learning', None)
        teacher_skill = (
            teacher_learning.skills.get('adult_meowing')
            if isinstance(teacher_learning, CatLearningState)
            else None
        )
        kitten_skill = (
            kitten_learning.skills.get('adult_meowing')
            if isinstance(kitten_learning, CatLearningState)
            else None
        )
        if teacher_skill is None or not teacher_skill.learned:
            return self._deny(teacher, kitten, vocalization, current_day, 'teacher_does_not_know_adult_meowing')
        if kitten_skill is None:
            return self._deny(teacher, kitten, vocalization, current_day, 'kitten_learning_state_unavailable')
        teacher_vocalizations = teacher_skill.vocalizations
        if not teacher_vocalizations.get(vocalization, False):
            return self._deny(teacher, kitten, vocalization, current_day, 'teacher_does_not_know_vocalization')
        kitten_vocalizations = kitten_skill.vocalizations
        if not kitten_vocalizations:
            kitten_vocalizations.update({
                name: False
                for name in CatLearning.ADULT_VOCALIZATIONS
            })
        if kitten_vocalizations.get(vocalization, False):
            return self._deny(teacher, kitten, vocalization, current_day, 'vocalization_already_learned')
        kitten_vocalizations[vocalization] = True
        learned_count = sum((1 for learned in kitten_vocalizations.values() if learned))
        total_count = len(CatLearning.ADULT_VOCALIZATIONS)
        kitten_skill.progress = learned_count / total_count
        completed = learned_count == total_count
        if completed:
            kitten_skill.learned = True
            kitten_skill.progress = 1.0
            kitten_skill.teacher = teacher.name
            kitten_skill.learned_on_day = current_day
            kitten_learning.adult_meowing_learned = True
        lesson = {'name': 'adult_vocalization_learned', 'teacher': teacher.name, 'student': kitten.name, 'vocalization': vocalization, 'day': current_day, 'learned_count': learned_count, 'total_count': total_count, 'adult_meowing_complete': completed}
        kitten_learning.lessons.append(lesson)
        event = {**lesson, 'taught': True}
        self.history.append(event)
        quantum_events = getattr(self.universe, 'quantum_events', None)
        if quantum_events is not None:
            quantum_events.append(event)
        return event

    def teach_all(self, teacher, kitten, current_day):
        results = []
        for vocalization in CatLearning.ADULT_VOCALIZATIONS:
            result = self.teach(teacher=teacher, kitten=kitten, vocalization=vocalization, current_day=current_day)
            results.append(result)
        return {'name': 'adult_vocalization_repertoire_taught', 'teacher': teacher.name, 'student': kitten.name, 'day': current_day, 'results': results, 'complete': kitten.learning.skills['adult_meowing'].learned}

    def _deny(self, teacher, kitten, vocalization, current_day, reason):
        event = {'name': 'adult_vocalization_lesson_denied', 'teacher': getattr(teacher, 'name', None), 'student': getattr(kitten, 'name', None), 'vocalization': vocalization, 'day': current_day, 'reason': reason, 'taught': False}
        self.history.append(event)
        return event
