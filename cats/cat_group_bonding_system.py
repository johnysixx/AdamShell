from copy import deepcopy

class CatGroupBondingSystem:

    def __init__(self, group_system):
        self.group_system = group_system

    def evaluate(self, group_id, cats):
        group = self.group_system._group(group_id)
        members = self.group_system._member_objects(group, cats)
        if len(members) < 2:
            return {'group_id': group_id, 'cohesion': 0.0, 'bonded_group': False, 'member_count': len(members)}
        trust_values = []
        affiliation_values = []
        tension_values = []
        scent_values = []
        for first in members:
            scent_values.append(float(first.group.shared_scent))
            for second in members:
                if first is second:
                    continue
                relation = first.relationships.get(second.name, {})
                trust_values.append(float(relation.get('trust', 0.5)))
                affiliation_values.append(float(relation.get('affiliation', 0.0)))
                tension_values.append(float(relation.get('tension', 0.0)))
        trust = self._average(trust_values)
        affiliation = self._average(affiliation_values)
        tension = self._average(tension_values)
        scent = self._average(scent_values)
        history_bonus = min(0.2, len(getattr(group, 'history', [])) * 0.01)
        cohesion = trust * 0.35 + affiliation * 0.25 + scent * 0.25 + history_bonus - tension * 0.4
        cohesion = self._clamp(cohesion)
        return {'group_id': group_id, 'cohesion': round(cohesion, 4), 'bonded_group': cohesion >= 0.65, 'member_count': len(members), 'trust': round(trust, 4), 'affiliation': round(affiliation, 4), 'tension': round(tension, 4), 'shared_scent': round(scent, 4)}

    def reinforce(self, group_id, cats, amount=0.05):
        group = self.group_system._group(group_id)
        members = self.group_system._member_objects(group, cats)
        amount = max(0.0, float(amount))
        scent_gain = amount * 0.75
        group.shared_scent_strength = self._clamp(float(getattr(group, 'shared_scent_strength', 0.0)) + scent_gain)
        for first in members:
            first.group.shared_scent = group.shared_scent_strength
            for second in members:
                if first is second:
                    continue
                relation = self.group_system._ensure_relationship(first, second)
                relation['familiarity'] = self._clamp(float(relation['familiarity']) + amount * 0.5)
                relation['trust'] = self._clamp(float(relation['trust']) + amount * 0.35)
                relation['affiliation'] = self._clamp(float(relation['affiliation']) + amount)
                relation['tension'] = self._clamp(float(relation['tension']) - amount * 0.5)
        event = {'name': 'cat_group_bond_reinforced', 'group_id': group_id, 'members': [cat.name for cat in members], 'amount': amount}
        group.history.append(deepcopy(event))
        for cat in members:
            cat.group.support_events += 1
            cat.social_interactions.append(deepcopy(event))
        result = self.evaluate(group_id, cats)
        return {**event, 'cohesion': result['cohesion'], 'bonded_group': result['bonded_group']}

    def _average(self, values):
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _clamp(self, value):
        return max(0.0, min(1.0, float(value)))
