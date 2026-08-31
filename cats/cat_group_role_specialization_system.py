from copy import deepcopy

class CatGroupRoleSpecializationSystem:
    SPECIALIZATIONS = {'guardian': {'night_guardian': {'required_traits': {'courage': 0.5}}, 'door_guardian': {'required_traits': {'courage': 0.4, 'curiosity': 0.25}}}, 'scout': {'scent_scout': {'required_traits': {'curiosity': 0.5}}, 'box_scout': {'required_traits': {'curiosity': 0.45, 'courage': 0.3}}}, 'storyteller': {'myth_keeper': {'required_traits': {'sociability': 0.45}}}, 'kitten_teacher': {'family_teacher': {'required_traits': {'sociability': 0.4}}}}

    def __init__(self, group_system):
        self.group_system = group_system

    def specialize(self, group_id, cat, base_role, specialization):
        group = self.group_system._group(group_id)
        if base_role not in cat.group_roles.active:
            return {'name': 'cat_role_specialization_denied', 'reason': 'base_role_not_held', 'specialized': False}
        profile = self.SPECIALIZATIONS.get(base_role, {}).get(specialization)
        if profile is None:
            return {'name': 'cat_role_specialization_denied', 'reason': 'unknown_specialization', 'specialized': False}
        traits = cat.personality.get('traits', {})
        for trait, minimum in profile['required_traits'].items():
            value = self._number(traits.get(trait, 0.5))
            if value < minimum:
                return {'name': 'cat_role_specialization_denied', 'reason': 'insufficient_trait', 'trait': trait, 'required': minimum, 'actual': value, 'specialized': False}
        group.role_specializations.setdefault(base_role, {})
        holders = group.role_specializations[base_role].setdefault(specialization, [])
        if cat.name not in holders:
            holders.append(cat.name)
        cat.group_roles.active[specialization] = {'group_id': group_id, 'base_role': base_role, 'specialized': True}
        event = {'name': 'cat_group_role_specialized', 'group_id': group_id, 'cat': cat.name, 'base_role': base_role, 'specialization': specialization, 'specialized': True}
        cat.group_roles.history.append(deepcopy(event))
        group.history.append(deepcopy(event))
        return event

    def specializations(self, group_id, base_role=None):
        group = self.group_system._group(group_id)
        if base_role is None:
            return deepcopy(group.role_specializations)
        return deepcopy(group.role_specializations.get(base_role, {}))

    def _number(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
