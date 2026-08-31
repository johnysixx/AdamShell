from copy import deepcopy

class CatGroupCultureSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def practice(self, group_id, practice, category, participants=None, weight=0.1):
        group = self.group_system._group(group_id)
        culture = group.culture
        traditions = culture.traditions
        tradition = traditions.setdefault(practice, {'name': practice, 'category': category, 'occurrences': 0, 'strength': 0.0})
        tradition['occurrences'] += 1
        tradition['strength'] = self._clamp(float(tradition['strength']) + float(weight))
        trait = self._trait_for_category(category)
        traits = culture.traits
        traits[trait] = self._clamp(float(traits.get(trait, 0.0)) + float(weight) * 0.5)
        event = {'name': 'cat_group_cultural_practice', 'group_id': group_id, 'practice': practice, 'category': category, 'participants': list(participants or []), 'strength': tradition['strength']}
        culture.history.append(deepcopy(event))
        group.history.append(deepcopy(event))
        return event

    def express_preference(self, group_id, preference, value, strength=0.1):
        group = self.group_system._group(group_id)
        preferences = group.culture.preferences
        record = preferences.setdefault(preference, {'value': value, 'strength': 0.0, 'expressions': 0})
        record['value'] = value
        record['expressions'] += 1
        record['strength'] = self._clamp(float(record['strength']) + float(strength))
        return {'name': 'cat_group_preference_expressed', 'group_id': group_id, 'preference': preference, 'value': value, 'strength': record['strength']}

    def profile(self, group_id):
        group = self.group_system._group(group_id)
        return deepcopy(group.culture)

    def _trait_for_category(self, category):
        mapping = {'exploration': 'curious', 'defense': 'protective', 'knowledge': 'scholarly', 'hunting': 'hunters', 'social': 'social', 'ritual': 'ritualized', 'navigation': 'wandering'}
        return mapping.get(category, 'distinctive')

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
