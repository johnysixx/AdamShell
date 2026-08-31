from copy import deepcopy
from uuid import uuid4
from cats.cat_group_diplomacy_system import CatGroupDiplomacySystem
from cats.cat_group_knowledge_system import CatGroupKnowledgeSystem
from cats.cat_federation import CatFederation

class CatGroupFederationSystem:

    def __init__(self, group_system):
        self.group_system = group_system
        self.federations = {}
        self.diplomacy = CatGroupDiplomacySystem(group_system)
        self.knowledge = CatGroupKnowledgeSystem(group_system)

    def create(self, founder_group_id, name=None):
        founder = self.group_system._group(founder_group_id)
        federation_id = 'cat_federation_' + uuid4().hex[:8]
        federation = CatFederation(**{'id': federation_id, 'name': name if name is not None else federation_id, 'founder_group': founder_group_id, 'groups': [founder_group_id], 'history': []})
        self.federations[federation_id] = federation
        founder.federations.append(federation_id)
        return {'name': 'cat_federation_created', 'federation_id': federation_id, 'founder_group': founder_group_id, 'created': True}

    def admit(self, federation_id, group_id):
        federation = self._federation(federation_id)
        group = self.group_system._group(group_id)
        if group_id in federation.groups:
            return {'name': 'cat_federation_admission_skipped', 'reason': 'already_member', 'admitted': False}
        relations = []
        for existing_group_id in federation.groups:
            relation = self.diplomacy.mutual_relation(existing_group_id, group_id)
            relations.append(relation['mutual_score'])
        average = sum(relations) / len(relations) if relations else 0.0
        if average < 0.0:
            return {'name': 'cat_federation_admission_denied', 'reason': 'negative_diplomacy', 'score': average, 'admitted': False}
        federation.groups.append(group_id)
        group.federations.append(federation_id)
        event = {'name': 'cat_group_joined_federation', 'federation_id': federation_id, 'group_id': group_id, 'admitted': True}
        federation.history.append(deepcopy(event))
        return event

    def share_knowledge(self, federation_id, source_group_id, knowledge_id):
        federation = self._federation(federation_id)
        if source_group_id not in federation.groups:
            return {'name': 'cat_federation_knowledge_denied', 'reason': 'source_not_member', 'shared': False}
        targets = []
        for group_id in federation.groups:
            if group_id == source_group_id:
                continue
            result = self.knowledge.transmit_between_groups(source_group_id, group_id, knowledge_id, transmission='federation')
            if result.get('transmitted', False):
                targets.append(group_id)
        return {'name': 'cat_federation_knowledge_shared', 'federation_id': federation_id, 'source_group': source_group_id, 'knowledge_id': knowledge_id, 'targets': targets, 'shared': True}

    def leave(self, federation_id, group_id):
        federation = self._federation(federation_id)
        group = self.group_system._group(group_id)
        if group_id not in federation.groups:
            return {'name': 'cat_federation_leave_denied', 'reason': 'not_member', 'left': False}
        federation.groups.remove(group_id)
        if federation_id in group.federations:
            group.federations.remove(federation_id)
        return {'name': 'cat_group_left_federation', 'federation_id': federation_id, 'group_id': group_id, 'left': True}

    def _federation(self, federation_id):
        federation = self.federations.get(federation_id)
        if federation is None:
            raise KeyError(f'Unknown federation: {federation_id}')
        return federation
