from copy import deepcopy
from uuid import uuid4
from cats.cat_culture_objects import CatInstitutionConflict

class CatGroupInstitutionalConflictSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def detect(self, group_id, first_institution, second_institution):
        group = self.group_system._group(group_id)
        first = group.institutions.get(first_institution)
        second = group.institutions.get(second_institution)
        if first is None or second is None:
            return {'name': 'cat_institution_conflict_detection_denied', 'reason': 'unknown_institution', 'conflict': False}
        shared_roles = sorted(set(first.get('roles', [])).intersection(second.get('roles', [])))
        shared_rituals = sorted(set(first.get('rituals', [])).intersection(second.get('rituals', [])))
        different_purpose = first.get('purpose') != second.get('purpose')
        score = len(shared_roles) * 0.3 + len(shared_rituals) * 0.15 + (0.15 if different_purpose and shared_roles else 0.0)
        score = min(1.0, score)
        if score >= 0.6:
            status = 'institutional_conflict'
        elif score >= 0.25:
            status = 'institutional_friction'
        else:
            status = 'institutionally_compatible'
        return {'name': 'cat_institution_conflict_detected', 'group_id': group_id, 'first_institution': first_institution, 'second_institution': second_institution, 'shared_roles': shared_roles, 'shared_rituals': shared_rituals, 'different_purpose': different_purpose, 'score': round(score, 4), 'status': status, 'conflict': status != 'institutionally_compatible'}

    def escalate(self, group_id, first_institution, second_institution, issue, intensity=0.5):
        group = self.group_system._group(group_id)
        first = group.institutions.get(first_institution)
        second = group.institutions.get(second_institution)
        if first is None or second is None:
            return {'name': 'cat_institution_conflict_denied', 'reason': 'unknown_institution', 'escalated': False}
        intensity = self._clamp(intensity)
        conflict_id = 'institution_conflict_' + uuid4().hex[:8]
        continuity_loss = 0.2 * intensity
        for institution in (first, second):
            institution.continuity = max(0.0, float(getattr(institution, 'continuity', 1.0)) - continuity_loss)
        conflict = CatInstitutionConflict(**{'id': conflict_id, 'first_institution': first_institution, 'second_institution': second_institution, 'issue': issue, 'intensity': intensity, 'resolved': False, 'mediator': None, 'history': []})
        group.institution_conflicts[conflict_id] = conflict
        event = {'name': 'cat_group_institutional_conflict', 'group_id': group_id, 'conflict_id': conflict_id, 'first_institution': first_institution, 'second_institution': second_institution, 'issue': issue, 'intensity': intensity, 'escalated': True}
        conflict.history.append(deepcopy(event))
        group.history.append(deepcopy(event))
        return event

    def mediate(self, group_id, conflict_id, mediator):
        group = self.group_system._group(group_id)
        conflict = group.institution_conflicts.get(conflict_id)
        if conflict is None:
            return {'name': 'cat_institution_mediation_denied', 'reason': 'unknown_conflict', 'mediated': False}
        if 'mediator' not in mediator.group_roles['active']:
            return {'name': 'cat_institution_mediation_denied', 'reason': 'cat_not_mediator', 'mediated': False}
        influence = float(mediator.group.influence)
        reduction = min(0.5, 0.15 + influence * 0.3)
        conflict.intensity = self._clamp(conflict.intensity - reduction)
        conflict.mediator = mediator.name
        if conflict.intensity <= 0.2:
            conflict.resolved = True
        if conflict.resolved:
            self._restore_institutions(group, conflict, amount=0.1)
        event = {'name': 'cat_institution_conflict_mediated', 'group_id': group_id, 'conflict_id': conflict_id, 'mediator': mediator.name, 'intensity': conflict.intensity, 'resolved': conflict.resolved, 'mediated': True}
        conflict.history.append(deepcopy(event))
        group.history.append(deepcopy(event))
        return event

    def institutional_split(self, group_id, conflict_id):
        group = self.group_system._group(group_id)
        conflict = group.institution_conflicts.get(conflict_id)
        if conflict is None:
            return {'name': 'cat_institution_split_denied', 'reason': 'unknown_conflict', 'split': False}
        if conflict.resolved or conflict.intensity < 0.75:
            return {'name': 'cat_institution_split_denied', 'reason': 'conflict_not_severe_enough', 'split': False}
        first = group.institutions[conflict.first_institution]
        second = group.institutions[conflict.second_institution]
        first['continuity'] = max(0.0, first['continuity'] - 0.25)
        second['continuity'] = max(0.0, second['continuity'] - 0.25)
        return {'name': 'cat_institutional_split', 'group_id': group_id, 'conflict_id': conflict_id, 'institutions': [conflict.first_institution, conflict.second_institution], 'split': True}

    def _restore_institutions(self, group, conflict, amount):
        for name in (conflict.first_institution, conflict.second_institution):
            institution = group.institutions[name]
            institution.continuity = min(1.0, float(institution.continuity) + amount)

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
