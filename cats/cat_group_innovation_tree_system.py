from copy import deepcopy

class CatGroupInnovationTreeSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def register(self, group_id, innovation_id, parent_innovation_id=None):
        group = self.group_system._group(group_id)
        innovation = group.innovations.get(innovation_id)
        if innovation is None:
            return {'name': 'cat_innovation_tree_denied', 'reason': 'unknown_innovation', 'registered': False}
        tree = group.innovation_tree
        tree[innovation_id] = {'innovation_id': innovation_id, 'parent': parent_innovation_id, 'children': [], 'generation': 0 if parent_innovation_id is None else int(tree.get(parent_innovation_id, {}).get('generation', 0)) + 1}
        if parent_innovation_id is not None and parent_innovation_id in tree:
            children = tree[parent_innovation_id]['children']
            if innovation_id not in children:
                children.append(innovation_id)
        innovation.parent_innovation = parent_innovation_id
        innovation.generation = tree[innovation_id]['generation']
        return {'name': 'cat_innovation_tree_registered', 'group_id': group_id, 'innovation_id': innovation_id, 'parent': parent_innovation_id, 'generation': innovation.generation, 'registered': True}

    def descendants(self, group_id, innovation_id):
        group = self.group_system._group(group_id)
        tree = group.innovation_tree
        if innovation_id not in tree:
            return []
        result = []
        stack = list(tree[innovation_id]['children'])
        while stack:
            current = stack.pop(0)
            result.append(current)
            stack.extend(tree.get(current, {}).get('children', []))
        return result

    def tree(self, group_id):
        group = self.group_system._group(group_id)
        return deepcopy(group.innovation_tree)
