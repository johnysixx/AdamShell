from copy import deepcopy
from cats.cat import Cat
from cats.cat_family_system import CatFamilySystem

class CatFamilyBondingSystem:

    def __init__(self, cats_layer=None):
        self.cats_layer = cats_layer
        self.family_system = CatFamilySystem(cats_layer)

    def evaluate(self, first, second):
        self._require_cat(first)
        self._require_cat(second)
        relation = self.family_system.relation(first, second)
        if relation is None:
            return {'related': False, 'eligible': False, 'relation': None, 'reason': 'not_family'}
        relationship = first.relationships.get(second.name, {})
        tension = self._number(relationship.get('tension', 0.0))
        care_events = max(int(getattr(first.maternal_care_received, 'care_events', 0)), int(getattr(second.maternal_care_received, 'care_events', 0)))
        play_events = max(int(first.sibling_play.partners.get(second.name, 0)), int(second.sibling_play.partners.get(first.name, 0)))
        parent_child = relation in {'mother', 'father', 'child'}
        siblings = relation in {'sibling', 'half_sibling', 'sibling_littermate', 'half_sibling_littermate'}
        eligible = bool(tension <= 0.5 and (parent_child and care_events >= 3 or (siblings and play_events >= 3)))
        return {'related': True, 'eligible': eligible, 'relation': relation, 'tension': tension, 'care_events': care_events, 'play_events': play_events}

    def form_bond(self, first, second):
        check_first = self.evaluate(first, second)
        check_second = self.evaluate(second, first)
        if not check_first['eligible'] or not check_second['eligible']:
            return {'name': 'cat_family_bond_not_formed', 'first': first.name, 'second': second.name, 'formed': False, 'reason': 'family_bond_requirements_not_met'}
        relation = check_first['relation']
        if relation in {'mother', 'father', 'child'}:
            strength = 0.8
        elif relation == 'sibling_littermate':
            strength = 0.75
        else:
            strength = 0.65
        self._store(first, second, relation, strength)
        reverse_relation = check_second['relation']
        self._store(second, first, reverse_relation, strength)
        event = {'name': 'cat_family_bond_formed', 'first': first.name, 'second': second.name, 'relation': relation, 'strength': strength, 'formed': True}
        self._record_both(first, second, event)
        return event

    def _store(self, cat, other_cat, relation, strength):
        existing = cat.bonds.get(other_cat.name, {})
        existing.update({'other_cat': other_cat.name, 'active': True, 'strength': max(self._number(existing.get('strength', 0.0)), strength), 'source': 'family', 'family_relation': relation})
        existing.setdefault('groom_count', 0)
        existing.setdefault('sleep_count', 0)
        existing.setdefault('follow_count', 0)
        cat.bonds[other_cat.name] = existing
        cat.family_bonding.events += 1
        if other_cat.name not in cat.family_bonding.family_bonds:
            cat.family_bonding.family_bonds.append(other_cat.name)

    def _record_both(self, first, second, event):
        first.social_interactions.append(deepcopy(event))
        second.social_interactions.append(deepcopy(event))

    def _number(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _require_cat(self, cat):
        if not isinstance(cat, Cat):
            raise TypeError('CatFamilyBondingSystem requires Cat.')
