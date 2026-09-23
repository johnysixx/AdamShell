from copy import deepcopy

from cats.cat_group_role_state import (
    CatGroupRoleAssignedEvent,
    CatGroupRoleReleasedEvent,
    CatGroupRoleState,
)

class CatGroupRoleSystem:
    ROLE_PROFILES = {'storyteller': {'traits': {'sociability': 0.45, 'curiosity': 0.35}, 'knowledge_weight': 0.2}, 'scout': {'traits': {'curiosity': 0.55, 'courage': 0.35}, 'knowledge_weight': 0.1}, 'guardian': {'traits': {'courage': 0.6}, 'influence_weight': 0.4}, 'kitten_teacher': {'traits': {'sociability': 0.4}, 'knowledge_weight': 0.35}, 'scent_keeper': {'traits': {'sociability': 0.3}, 'group_scent_weight': 0.5}, 'mediator': {'traits': {'sociability': 0.55}, 'influence_weight': 0.3}}

    def __init__(self, group_system):
        self.group_system = group_system

    def suitability(self, group_id, cat, role):
        group = self.group_system._group(group_id)
        if cat.name not in group.members:
            return {'role': role, 'eligible': False, 'score': 0.0, 'reason': 'not_group_member'}
        profile = self.ROLE_PROFILES.get(role)
        if profile is None:
            return {'role': role, 'eligible': False, 'score': 0.0, 'reason': 'unknown_role'}
        traits = cat.personality.traits
        score = 0.0
        for trait, weight in profile.get('traits', {}).items():
            score += self._number(getattr(traits, trait, 0.5)) * weight
        score += self._number(cat.group.influence) * profile.get('influence_weight', 0.0)
        score += cat.knowledge.role_knowledge_score() * profile.get('knowledge_weight', 0.0)
        score += self._number(cat.group.shared_scent) * profile.get('group_scent_weight', 0.0)
        score = min(1.0, score)
        return {'role': role, 'eligible': score >= 0.35, 'score': round(score, 4)}

    def assign(self, group_id, cat, role):
        check = self.suitability(group_id, cat, role)
        if not check['eligible']:
            return {'name': 'cat_group_role_denied', 'group_id': group_id, 'cat': cat.name, 'role': role, 'reason': check.get('reason', 'insufficient_suitability'), 'assigned': False}
        existing = cat.group_roles.active.get(
            role
        )

        if (
            existing is not None
            and not isinstance(
                existing,
                CatGroupRoleState,
            )
        ):
            raise TypeError(
                'Cat group role record must be '
                'CatGroupRoleState.'
            )

        if existing is None:
            existing = CatGroupRoleState()

        group = self.group_system._group(
            group_id
        )

        holders = group.roles.setdefault(
            role,
            []
        )

        if cat.name not in holders:
            holders.append(
                cat.name
            )

        existing.assign_base(
            group_id=group_id,
            score=check['score'],
        )

        cat.group_roles.active[
            role
        ] = existing

        cat.group_roles.role_events += 1

        event = CatGroupRoleAssignedEvent(
            group_id=group_id,
            cat=cat.name,
            role=role,
            score=check['score'],
        )

        cat.group_roles.record_event(
            event
        )

        snapshot = event.to_dict()

        group.history.append(
            deepcopy(snapshot)
        )

        return snapshot

    def release(self, group_id, cat, role, reason='role_released'):
        group = self.group_system._group(group_id)
        holders = group.roles.get(role, [])
        if cat.name in holders:
            holders.remove(cat.name)
        cat.group_roles.active.pop(
            role,
            None,
        )

        event = CatGroupRoleReleasedEvent(
            group_id=group_id,
            cat=cat.name,
            role=role,
            reason=reason,
        )

        cat.group_roles.record_event(
            event
        )

        return event.to_dict()

    def holders(self, group_id, role):
        group = self.group_system._group(group_id)
        return list(group.roles.get(role, []))

    def _number(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
