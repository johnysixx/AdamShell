from copy import deepcopy

class CatGroupMemorySystem:
    MAX_RECENT_EVENTS = 12

    def __init__(self, group_system):
        self.group_system = group_system

    def remember_encounter(self, first_group_id, second_group_id, event):
        first = self.group_system._group(first_group_id)
        second = self.group_system._group(second_group_id)
        first_memory = self._memory(first, second_group_id)
        second_memory = self._memory(second, first_group_id)
        self._apply(first_memory, event, own_group_id=first_group_id)
        self._apply(second_memory, event, own_group_id=second_group_id)
        return {'name': 'cat_group_encounter_remembered', 'first_group': first_group_id, 'second_group': second_group_id, 'remembered': True}

    def record_cooperation(self, first_group_id, second_group_id, cooperation_type):
        event = {'name': 'cat_group_cooperation', 'first_group': first_group_id, 'second_group': second_group_id, 'cooperation_type': cooperation_type, 'conflict': False, 'cooperation': True}
        self.remember_encounter(first_group_id, second_group_id, event)
        return event

    def record_betrayal(self, betrayer_group_id, victim_group_id, reason):
        event = {'name': 'cat_group_betrayal', 'betrayer': betrayer_group_id, 'victim': victim_group_id, 'reason': reason, 'betrayal': True}
        self.remember_encounter(betrayer_group_id, victim_group_id, event)
        return event

    def relation_memory(self, group_id, other_group_id):
        group = self.group_system._group(group_id)
        return deepcopy(self._memory(group, other_group_id))

    def _memory(self, group, other_group_id):
        return group.group_memory.setdefault(other_group_id, {'encounters': 0, 'peaceful_encounters': 0, 'conflicts': 0, 'victories': 0, 'defeats': 0, 'standoffs': 0, 'cooperations': 0, 'betrayals': 0, 'last_outcome': None, 'recent_events': []})

    def _apply(self, memory, event, own_group_id):
        memory['encounters'] += 1
        if event.get('betrayal', False):
            memory['betrayals'] += 1
            outcome = 'betrayal'
        elif event.get('cooperation', False):
            memory['cooperations'] += 1
            outcome = 'cooperation'
        elif event.get('conflict', False):
            memory['conflicts'] += 1
            winner = event.get('winner')
            loser = event.get('loser')
            if winner is None:
                memory['standoffs'] += 1
                outcome = 'standoff'
            elif winner == own_group_id:
                memory['victories'] += 1
                outcome = 'victory'
            elif loser == own_group_id:
                memory['defeats'] += 1
                outcome = 'defeat'
            else:
                outcome = 'conflict'
        else:
            memory['peaceful_encounters'] += 1
            outcome = 'peaceful'
        memory['last_outcome'] = outcome
        recent = list(memory.get('recent_events', []))
        recent.append(outcome)
        memory['recent_events'] = recent[-self.MAX_RECENT_EVENTS:]
