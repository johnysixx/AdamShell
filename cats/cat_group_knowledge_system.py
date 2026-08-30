from copy import deepcopy
from cats.cat_social_objects import CatGroupKnowledgeRecord

class CatGroupKnowledgeSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def contribute(self, group_id, cat, knowledge_id, content, category, confidence=1.0, verified=True, source_type='personal_experience'):
        group = self.group_system._group(group_id)
        if cat.name not in group.members:
            return {'name': 'cat_group_knowledge_contribution_denied', 'reason': 'cat_not_group_member', 'contributed': False}
        confidence = self._clamp(confidence)
        existing = group.knowledge.get(knowledge_id)
        record = CatGroupKnowledgeRecord(**{'knowledge_id': knowledge_id, 'category': category, 'content': deepcopy(content), 'origin_cat': cat.name, 'origin_group': group_id, 'source_type': source_type, 'confidence': confidence, 'verified': bool(verified), 'verification_count': 1 if verified else 0, 'contradiction_count': 0, 'transmission_path': [{'type': source_type, 'source': cat.name, 'group': group_id}]})
        if existing is not None:
            record.verification_count += int(existing.get('verification_count', 0))
            record.contradiction_count += int(existing.get('contradiction_count', 0))
        group.knowledge[knowledge_id] = record
        self._offer_to_member(cat, record, transmission='personal_experience')
        event = {'name': 'cat_group_knowledge_contributed', 'group_id': group_id, 'cat': cat.name, 'knowledge_id': knowledge_id, 'category': category, 'confidence': confidence, 'verified': bool(verified), 'contributed': True}
        group.history.append(deepcopy(event))
        return event

    def share_with_group_members(self, group_id, cats, knowledge_id):
        group = self.group_system._group(group_id)
        record = group.knowledge.get(knowledge_id)
        if record is None:
            return {'name': 'cat_group_knowledge_share_denied', 'reason': 'unknown_knowledge', 'shared': False}
        members = self.group_system._member_objects(group, cats)
        receivers = []
        for cat in members:
            self._offer_to_member(cat, record, transmission='own_group')
            receivers.append(cat.name)
        return {'name': 'cat_group_knowledge_shared', 'group_id': group_id, 'knowledge_id': knowledge_id, 'receivers': receivers, 'shared': True}

    def transmit_between_groups(self, source_group_id, target_group_id, knowledge_id, transmission='allied_group'):
        source = self.group_system._group(source_group_id)
        target = self.group_system._group(target_group_id)
        record = source['knowledge'].get(knowledge_id)
        if record is None:
            return {'name': 'cat_group_knowledge_transmission_denied', 'reason': 'source_does_not_know', 'transmitted': False}
        copied = deepcopy(record)
        copied['confidence'] = self._clamp(float(copied.get('confidence', 0.0)) * 0.88)
        copied['verified'] = False
        copied['transmission_path'].append({'type': transmission, 'source_group': source_group_id, 'target_group': target_group_id})
        existing = target['knowledge'].get(knowledge_id)
        if existing is None:
            target['knowledge'][knowledge_id] = copied
        elif copied['confidence'] > float(existing.get('confidence', 0.0)):
            target['knowledge'][knowledge_id] = copied
        event = {'name': 'cat_group_knowledge_transmitted', 'source_group': source_group_id, 'target_group': target_group_id, 'knowledge_id': knowledge_id, 'confidence': copied['confidence'], 'transmission': transmission, 'transmitted': True}
        source['history'].append(deepcopy(event))
        target['history'].append(deepcopy(event))
        return event

    def propagate_to_members(self, group_id, cats, knowledge_id):
        group = self.group_system._group(group_id)
        record = group.knowledge.get(knowledge_id)
        if record is None:
            return {'name': 'cat_group_knowledge_propagation_denied', 'reason': 'unknown_knowledge', 'propagated': False}
        receivers = []
        for cat in self.group_system._member_objects(group, cats):
            self._offer_to_member(cat, record, transmission='group_propagation')
            receivers.append(cat.name)
        return {'name': 'cat_group_knowledge_propagated', 'group_id': group_id, 'knowledge_id': knowledge_id, 'receivers': receivers, 'propagated': True}

    def verify(self, group_id, cat, knowledge_id, confirmed):
        group = self.group_system._group(group_id)
        record = group.knowledge.get(knowledge_id)
        if record is None:
            return {'name': 'cat_group_knowledge_verification_denied', 'reason': 'unknown_knowledge', 'verified': False}
        if confirmed:
            record.verification_count += 1
            record.confidence = self._clamp(float(record.confidence) + 0.12)
            record.verified = True
            outcome = 'confirmed'
        else:
            record.contradiction_count += 1
            record.confidence = self._clamp(float(record.confidence) - 0.25)
            if record.confidence < 0.35:
                record.verified = False
            outcome = 'contradicted'
        member_knowledge = cat.knowledge.setdefault('group_received_knowledge', {})
        personal = member_knowledge.get(knowledge_id)
        if personal is not None:
            personal['confidence'] = record.confidence
            personal['verified'] = bool(confirmed)
            personal['verified_by'] = cat.name
        event = {'name': 'cat_group_knowledge_verified', 'group_id': group_id, 'cat': cat.name, 'knowledge_id': knowledge_id, 'outcome': outcome, 'confidence': record.confidence}
        group.history.append(deepcopy(event))
        return event

    def _offer_to_member(self, cat, record, transmission):
        received = cat.knowledge.setdefault('group_received_knowledge', {})
        copy = deepcopy(record)
        if transmission != 'personal_experience':
            copy['verified'] = False
        copy['received_via'] = transmission
        received[record.knowledge_id] = copy
        return copy

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
