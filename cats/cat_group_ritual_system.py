from cats.cat_group_ritual_evolution_system import CatGroupRitualEvolutionSystem
from copy import deepcopy
from cats.cat_culture_objects import CatGroupRitual

class CatGroupRitualSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def define(self, group_id, ritual_name, category, required_roles=None):
        group = self.group_system._group(group_id)
        ritual = CatGroupRitual(**{'name': ritual_name, 'category': category, 'required_roles': list(required_roles or []), 'performances': 0, 'strength': 0.0, 'last_participants': []})
        group.rituals[ritual_name] = ritual
        CatGroupRitualEvolutionSystem(self.group_system).register_origin(group_id, ritual_name)
        return {'name': 'cat_group_ritual_defined', 'group_id': group_id, 'ritual': ritual_name, 'defined': True}

    def perform(self, group_id, ritual_name, participants):
        group = self.group_system._group(group_id)
        ritual = group.rituals.get(ritual_name)
        if ritual is None:
            return {'name': 'cat_group_ritual_denied', 'reason': 'unknown_ritual', 'performed': False}
        participant_names = [cat.name for cat in participants if cat.name in group.members]
        if not participant_names:
            return {'name': 'cat_group_ritual_denied', 'reason': 'no_group_participants', 'performed': False}
        ritual.performances += 1
        ritual.strength = min(1.0, float(ritual.strength) + 0.1)
        ritual.last_participants = participant_names
        culture = group.culture
        tradition = culture['traditions'].setdefault(ritual_name, {'name': ritual_name, 'category': 'ritual', 'occurrences': 0, 'strength': 0.0})
        tradition['occurrences'] += 1
        tradition['strength'] = min(1.0, float(tradition['strength']) + 0.08)
        event = {'name': 'cat_group_ritual_performed', 'group_id': group_id, 'ritual': ritual_name, 'participants': participant_names, 'strength': ritual.strength, 'performed': True}
        group.history.append(deepcopy(event))
        for cat in participants:
            if cat.name in participant_names:
                cat.social_interactions.append(deepcopy(event))
        return event
