from copy import deepcopy

class CatGroupMythLineageSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def register_origin(self, group_id, myth_id):
        group = self.group_system._group(group_id)
        myth = group.myths.get(myth_id)
        if myth is None:
            return {'name': 'cat_myth_lineage_denied', 'reason': 'unknown_myth', 'registered': False}
        lineage = group.myth_lineages.setdefault(myth_id, {'root_myth': myth_id, 'versions': [], 'children': {}})
        if myth_id not in lineage['versions']:
            lineage['versions'].append(myth_id)
        myth.lineage_root = myth_id
        myth.parent_version = None
        myth.generation = 0
        return {'name': 'cat_myth_lineage_registered', 'group_id': group_id, 'myth_id': myth_id, 'registered': True}

    def register_descendant(self, group_id, root_myth_id, parent_myth_id, child_myth_id):
        group = self.group_system._group(group_id)
        lineage = group.myth_lineages.setdefault(root_myth_id, {'root_myth': root_myth_id, 'versions': [], 'children': {}})
        if child_myth_id not in lineage['versions']:
            lineage['versions'].append(child_myth_id)
        lineage['children'].setdefault(parent_myth_id, [])
        if child_myth_id not in lineage['children'][parent_myth_id]:
            lineage['children'][parent_myth_id].append(child_myth_id)
        return {'name': 'cat_myth_descendant_registered', 'group_id': group_id, 'root_myth_id': root_myth_id, 'parent_myth_id': parent_myth_id, 'child_myth_id': child_myth_id, 'registered': True}

    def lineage(self, group_id, root_myth_id):
        group = self.group_system._group(group_id)
        return deepcopy(group.myth_lineages.get(root_myth_id))
