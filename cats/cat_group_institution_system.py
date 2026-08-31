from copy import deepcopy
from cats.cat_culture_objects import CatGroupInstitution

class CatGroupInstitutionSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def establish(self, group_id, institution_name, purpose, roles, rituals):
        group = self.group_system._group(group_id)
        institution = CatGroupInstitution(**{'name': institution_name, 'purpose': purpose, 'roles': list(roles), 'rituals': list(rituals), 'continuity': 1.0, 'generations': 0, 'active': True})
        group.institutions[institution_name] = institution
        event = {'name': 'cat_group_institution_established', 'group_id': group_id, 'institution': institution_name, 'purpose': purpose, 'established': True}
        group.history.append(deepcopy(event))
        return event

    def maintain(self, group_id, institution_name):
        group = self.group_system._group(group_id)
        institution = group.institutions.get(institution_name)
        if institution is None:
            return {'name': 'cat_group_institution_maintenance_denied', 'reason': 'unknown_institution', 'maintained': False}
        roles_present = all((bool(group.roles.get(role)) for role in institution.roles))
        rituals_present = all((ritual in group.rituals and group.rituals[ritual].performances > 0 for ritual in institution.rituals))
        if roles_present and rituals_present:
            institution.continuity = min(1.0, float(institution.continuity) + 0.05)
            institution.generations += 1
            status = 'maintained'
        else:
            institution.continuity = max(0.0, float(institution.continuity) - 0.15)
            status = 'weakened'
        if institution.continuity <= 0.1:
            institution.active = False
        return {'name': 'cat_group_institution_maintained', 'group_id': group_id, 'institution': institution_name, 'status': status, 'continuity': institution.continuity, 'active': institution.active, 'maintained': True}

    def transfer_after_split(self, parent_group_id, child_group_id, retention=0.65):
        parent = self.group_system._group(parent_group_id)
        child = self.group_system._group(child_group_id)
        inherited = []
        for name, institution in parent.institutions.items():
            copied = deepcopy(institution)
            copied.continuity = max(0.0, min(1.0, float(copied.continuity) * retention))
            copied.generations += 1
            copied.inherited_from = parent_group_id
            child.institutions[name] = copied
            inherited.append(name)
        return {'name': 'cat_group_institutions_inherited', 'parent_group': parent_group_id, 'child_group': child_group_id, 'institutions': inherited}
