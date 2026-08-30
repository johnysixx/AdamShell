from copy import deepcopy

class CatGroupCulturalConflictSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def compare(self, first_group_id, second_group_id):
        first = self.group_system._group(first_group_id)
        second = self.group_system._group(second_group_id)
        first_culture = first['culture']
        second_culture = second['culture']
        conflicts = []
        agreements = []
        first_preferences = first_culture['preferences']
        second_preferences = second_culture['preferences']
        shared_preferences = set(first_preferences).intersection(second_preferences)
        for name in shared_preferences:
            first_value = first_preferences[name].get('value')
            second_value = second_preferences[name].get('value')
            if first_value == second_value:
                agreements.append(name)
            else:
                conflicts.append({'type': 'preference', 'name': name, 'first': first_value, 'second': second_value})
        first_traits = first_culture['traits']
        second_traits = second_culture['traits']
        trait_keys = set(first_traits).union(second_traits)
        trait_distance = 0.0
        for key in trait_keys:
            trait_distance += abs(self._number(first_traits.get(key, 0.0)) - self._number(second_traits.get(key, 0.0)))
        if trait_keys:
            trait_distance /= len(trait_keys)
        conflict_score = min(1.0, len(conflicts) * 0.2 + trait_distance * 0.6)
        if conflict_score >= 0.7:
            status = 'cultural_conflict'
        elif conflict_score >= 0.35:
            status = 'cultural_friction'
        else:
            status = 'culturally_compatible'
        return {'first_group': first_group_id, 'second_group': second_group_id, 'status': status, 'conflict_score': round(conflict_score, 4), 'preference_conflicts': conflicts, 'agreements': agreements, 'trait_distance': round(trait_distance, 4)}

    def interact(self, first_group_id, second_group_id):
        result = self.compare(first_group_id, second_group_id)
        first = self.group_system._group(first_group_id)
        second = self.group_system._group(second_group_id)
        if result['status'] == 'cultural_conflict':
            diplomacy_delta = -0.2
        elif result['status'] == 'cultural_friction':
            diplomacy_delta = -0.08
        else:
            diplomacy_delta = 0.05
        for group, other_id in ((first, second_group_id), (second, first_group_id)):
            diplomacy = group.diplomacy.get(other_id)
            if diplomacy is not None:
                diplomacy['score'] = max(-1.0, min(1.0, self._number(diplomacy.get('score', 0.0)) + diplomacy_delta))
        event = {'name': 'cat_group_cultural_interaction', **result, 'diplomacy_delta': diplomacy_delta}
        first['history'].append(deepcopy(event))
        second['history'].append(deepcopy(event))
        return event

    def _number(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
