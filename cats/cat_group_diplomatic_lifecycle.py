from copy import deepcopy

class CatGroupDiplomaticLifecycle:

    def __init__(self, group_system):
        self.group_system = group_system

    def advance_relation(self, group_id, other_group_id):
        group = self.group_system._group(group_id)
        memory = group.group_memory.get(other_group_id)
        if memory is None:
            return {'name': 'cat_group_diplomacy_decay_skipped', 'reason': 'no_shared_history', 'advanced': False}
        before = deepcopy(memory)
        if memory['conflicts'] > 0:
            memory['conflicts'] -= 1
        if memory['defeats'] > 0:
            memory['defeats'] -= 1
        if memory['peaceful_encounters'] > 0:
            memory['peaceful_encounters'] -= 1
        if memory['cooperations'] > 0 and memory['encounters'] % 2 == 0:
            memory['cooperations'] -= 1
        event = {'name': 'cat_group_diplomacy_memory_aged', 'group_id': group_id, 'other_group_id': other_group_id, 'before': before, 'after': deepcopy(memory), 'advanced': True}
        group.history.append(deepcopy(event))
        return event

    def recover_from_betrayal(self, group_id, other_group_id):
        group = self.group_system._group(group_id)
        memory = group.group_memory.get(other_group_id)
        if memory is None:
            return {'name': 'cat_group_betrayal_recovery_denied', 'reason': 'no_shared_history', 'recovered': False}
        if memory['betrayals'] <= 0:
            return {'name': 'cat_group_betrayal_recovery_skipped', 'reason': 'no_betrayal', 'recovered': False}
        if memory['cooperations'] < 3:
            return {'name': 'cat_group_betrayal_recovery_denied', 'reason': 'insufficient_new_cooperation', 'recovered': False}
        memory['betrayals'] -= 1
        return {'name': 'cat_group_betrayal_recovered', 'group_id': group_id, 'other_group_id': other_group_id, 'remaining_betrayals': memory['betrayals'], 'recovered': True}
