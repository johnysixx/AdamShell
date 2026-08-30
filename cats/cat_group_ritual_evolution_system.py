from copy import deepcopy
from uuid import uuid4

class CatGroupRitualEvolutionSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def register_origin(self, group_id, ritual_name):
        group = self.group_system._group(group_id)
        ritual = group.rituals.get(ritual_name)
        if ritual is None:
            return {'name': 'cat_ritual_lineage_denied', 'reason': 'unknown_ritual', 'registered': False}
        lineage = group.ritual_lineages.setdefault(ritual_name, {'root_ritual': ritual_name, 'versions': [], 'children': {}})
        if ritual_name not in lineage['versions']:
            lineage['versions'].append(ritual_name)
        ritual.lineage_root = ritual_name
        ritual.parent_ritual = None
        ritual.generation = 0
        return {'name': 'cat_ritual_lineage_registered', 'group_id': group_id, 'ritual': ritual_name, 'registered': True}

    def mutate(self, group_id, ritual_name, new_name, category=None, required_roles=None, mutation_reason='local_adaptation'):
        group = self.group_system._group(group_id)
        parent = group.rituals.get(ritual_name)
        if parent is None:
            return {'name': 'cat_ritual_mutation_denied', 'reason': 'unknown_parent_ritual', 'mutated': False}
        if new_name in group.rituals:
            return {'name': 'cat_ritual_mutation_denied', 'reason': 'ritual_name_exists', 'mutated': False}
        root = parent.get('lineage_root', ritual_name)
        child = deepcopy(parent)
        child['name'] = new_name
        child['category'] = category if category is not None else parent.get('category')
        if required_roles is not None:
            child['required_roles'] = list(required_roles)
        child['performances'] = 0
        child['strength'] = max(0.0, float(parent.get('strength', 0.0)) * 0.7)
        child['lineage_root'] = root
        child['parent_ritual'] = ritual_name
        child['generation'] = int(parent.get('generation', 0)) + 1
        child['mutation_reason'] = mutation_reason
        group.rituals[new_name] = child
        lineage = group.ritual_lineages.setdefault(root, {'root_ritual': root, 'versions': [root], 'children': {}})
        if new_name not in lineage['versions']:
            lineage['versions'].append(new_name)
        lineage['children'].setdefault(ritual_name, [])
        if new_name not in lineage['children'][ritual_name]:
            lineage['children'][ritual_name].append(new_name)
        event = {'name': 'cat_group_ritual_mutated', 'group_id': group_id, 'parent_ritual': ritual_name, 'new_ritual': new_name, 'lineage_root': root, 'generation': child['generation'], 'reason': mutation_reason, 'mutated': True}
        group.history.append(deepcopy(event))
        return event

    def lineage(self, group_id, root_ritual):
        group = self.group_system._group(group_id)
        return deepcopy(group.ritual_lineages.get(root_ritual))
