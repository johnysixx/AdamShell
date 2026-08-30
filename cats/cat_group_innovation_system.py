from cats.cat_group_innovation_tree_system import CatGroupInnovationTreeSystem
from copy import deepcopy
from uuid import uuid4
from cats.cat_culture_objects import CatGroupInnovation

class CatGroupInnovationSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def combine(self, group_id, knowledge_ids, name, category, procedure, parent_innovation_id=None):
        group = self.group_system._group(group_id)
        knowledge_ids = list(dict.fromkeys(knowledge_ids))
        if len(knowledge_ids) < 2:
            return {'name': 'cat_group_innovation_denied', 'reason': 'at_least_two_knowledge_sources_required', 'created': False}
        sources = []
        for knowledge_id in knowledge_ids:
            record = group.knowledge.get(knowledge_id)
            if record is None:
                return {'name': 'cat_group_innovation_denied', 'reason': 'missing_knowledge', 'missing': knowledge_id, 'created': False}
            sources.append(record)
        confidence = sum((float(source.get('confidence', 0.0)) for source in sources)) / len(sources)
        confidence *= 0.7
        innovation_id = 'cat_innovation_' + uuid4().hex[:8]
        innovation = CatGroupInnovation(**{'innovation_id': innovation_id, 'name': name, 'category': category, 'source_knowledge': knowledge_ids, 'procedure': deepcopy(procedure), 'origin_group': group_id, 'confidence': self._clamp(confidence), 'verified': False, 'successful_trials': 0, 'failed_trials': 0})
        group.innovations[innovation_id] = innovation
        CatGroupInnovationTreeSystem(self.group_system).register(group_id, innovation_id, parent_innovation_id=parent_innovation_id)
        group.knowledge[innovation_id] = {'knowledge_id': innovation_id, 'category': category, 'content': deepcopy(procedure), 'origin_cat': None, 'origin_group': group_id, 'source_type': 'innovation', 'confidence': innovation.confidence, 'verified': False, 'verification_count': 0, 'contradiction_count': 0, 'transmission_path': [{'type': 'innovation', 'group': group_id}]}
        event = {'name': 'cat_group_innovation_created', 'group_id': group_id, 'innovation_id': innovation_id, 'innovation_name': name, 'sources': knowledge_ids, 'confidence': innovation.confidence, 'created': True}
        group.history.append(deepcopy(event))
        return event

    def trial(self, group_id, innovation_id, success):
        group = self.group_system._group(group_id)
        innovation = group.innovations.get(innovation_id)
        if innovation is None:
            return {'name': 'cat_group_innovation_trial_denied', 'reason': 'unknown_innovation', 'tested': False}
        if success:
            innovation.successful_trials += 1
            innovation.confidence = self._clamp(innovation.confidence + 0.15)
        else:
            innovation.failed_trials += 1
            innovation.confidence = self._clamp(innovation.confidence - 0.2)
        if innovation.successful_trials >= 2 and innovation.confidence >= 0.7:
            innovation.verified = True
        knowledge = group.knowledge[innovation_id]
        knowledge['confidence'] = innovation.confidence
        knowledge['verified'] = innovation.verified
        if success:
            knowledge['verification_count'] += 1
        else:
            knowledge['contradiction_count'] += 1
        return {'name': 'cat_group_innovation_trial', 'group_id': group_id, 'innovation_id': innovation_id, 'success': bool(success), 'confidence': innovation.confidence, 'verified': innovation.verified, 'tested': True}

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
