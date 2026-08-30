from cats.cat_group_myth_lineage_system import CatGroupMythLineageSystem
from copy import deepcopy
from uuid import uuid4
from cats.cat_culture_objects import CatGroupMyth

class CatGroupMythSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def create_from_knowledge(self, group_id, knowledge_id, title=None, interpretation=None):
        group = self.group_system._group(group_id)
        knowledge = group.knowledge.get(knowledge_id)
        if knowledge is None:
            return {'name': 'cat_group_myth_creation_denied', 'reason': 'unknown_knowledge', 'created': False}
        myth_id = 'cat_myth_' + uuid4().hex[:8]
        myth = CatGroupMyth(**{'myth_id': myth_id, 'title': title if title is not None else knowledge_id, 'source_knowledge': knowledge_id, 'origin_group': group_id, 'interpretation': deepcopy(interpretation) if interpretation is not None else deepcopy(knowledge['content']), 'credibility': self._clamp(float(knowledge.get('confidence', 0.5)) * 0.75), 'verified': False, 'retellings': 0, 'transformations': 0, 'transmission_path': [group_id]})
        group.myths[myth_id] = myth
        CatGroupMythLineageSystem(self.group_system).register_origin(group_id, myth_id)
        event = {'name': 'cat_group_myth_created', 'group_id': group_id, 'myth_id': myth_id, 'source_knowledge': knowledge_id, 'created': True}
        group.history.append(deepcopy(event))
        return event

    def retell(self, source_group_id, target_group_id, myth_id, transformation=None):
        source = self.group_system._group(source_group_id)
        target = self.group_system._group(target_group_id)
        myth = source['myths'].get(myth_id)
        if myth is None:
            return {'name': 'cat_group_myth_retelling_denied', 'reason': 'unknown_myth', 'retold': False}
        copied = deepcopy(myth)
        parent_myth_id = myth_id
        root_myth_id = copied.get('lineage_root', myth_id)
        if transformation is not None:
            new_myth_id = 'cat_myth_' + uuid4().hex[:8]
        else:
            new_myth_id = myth_id
        copied['myth_id'] = new_myth_id
        copied['lineage_root'] = root_myth_id
        copied['parent_version'] = parent_myth_id if new_myth_id != myth_id else copied.get('parent_version')
        copied['generation'] = int(copied.get('generation', 0)) + (1 if new_myth_id != myth_id else 0)
        copied['retellings'] += 1
        copied['credibility'] = self._clamp(float(copied['credibility']) * 0.92)
        copied['transmission_path'].append(target_group_id)
        if transformation is not None:
            copied['interpretation'] = deepcopy(transformation)
            copied['transformations'] += 1
            copied['credibility'] = self._clamp(copied['credibility'] * 0.85)
        copied['verified'] = False
        target['myths'][new_myth_id] = copied
        lineage_system = CatGroupMythLineageSystem(self.group_system)
        if root_myth_id not in target['myth_lineages']:
            target['myth_lineages'][root_myth_id] = {'root_myth': root_myth_id, 'versions': [root_myth_id], 'children': {}}
        if new_myth_id != parent_myth_id:
            lineage_system.register_descendant(target_group_id, root_myth_id, parent_myth_id, new_myth_id)
        return {'name': 'cat_group_myth_retold', 'source_group': source_group_id, 'target_group': target_group_id, 'myth_id': new_myth_id, 'parent_myth_id': parent_myth_id, 'root_myth_id': root_myth_id, 'credibility': copied['credibility'], 'transformed': transformation is not None, 'retold': True}

    def tell_members(self, group_id, cats, myth_id):
        group = self.group_system._group(group_id)
        myth = group.myths.get(myth_id)
        if myth is None:
            return {'name': 'cat_group_myth_telling_denied', 'reason': 'unknown_myth', 'told': False}
        listeners = []
        for cat in self.group_system._member_objects(group, cats):
            heard = cat.knowledge.setdefault('heard_group_myths', {})
            personal = deepcopy(myth)
            personal['heard_from_group'] = group_id
            personal['personally_verified'] = False
            heard[myth_id] = personal
            listeners.append(cat.name)
        return {'name': 'cat_group_myth_told', 'group_id': group_id, 'myth_id': myth_id, 'listeners': listeners, 'told': True}

    def verify_against_knowledge(self, group_id, myth_id):
        group = self.group_system._group(group_id)
        myth = group.myths.get(myth_id)
        if myth is None:
            return {'name': 'cat_group_myth_verification_denied', 'reason': 'unknown_myth', 'verified': False}
        knowledge = group.knowledge.get(myth.source_knowledge)
        if knowledge is None:
            return {'name': 'cat_group_myth_verification_denied', 'reason': 'source_knowledge_missing', 'verified': False}
        myth.verified = bool(knowledge.get('verified', False))
        if myth.verified:
            myth.credibility = self._clamp(max(myth.credibility, float(knowledge.get('confidence', 0.0))))
        return {'name': 'cat_group_myth_verified', 'group_id': group_id, 'myth_id': myth_id, 'verified': myth.verified, 'credibility': myth.credibility}

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
