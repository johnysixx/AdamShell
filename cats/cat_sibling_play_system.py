from copy import deepcopy
from cats.cat import Cat
from cats.cat_family_system import CatFamilySystem

class CatSiblingPlaySystem:
    MIN_PLAY_AGE_DAYS = 21

    def __init__(self, cats_layer=None):
        self.cats_layer = cats_layer
        self.family_system = CatFamilySystem(cats_layer)

    def can_play(self, first, second, age_days):
        self._require_cat(first)
        self._require_cat(second)
        relation = self.family_system.relation(first, second)
        littermates = relation in {'sibling_littermate', 'half_sibling_littermate'}
        same_layer = first.current_layer == second.current_layer
        return {'first': first.name, 'second': second.name, 'relation': relation, 'littermates': littermates, 'old_enough': int(age_days) >= self.MIN_PLAY_AGE_DAYS, 'same_layer': same_layer, 'allowed': littermates and same_layer and (int(age_days) >= self.MIN_PLAY_AGE_DAYS)}

    def play(self, first, second, age_days, current_day=None):
        check = self.can_play(first, second, age_days)
        if not check['allowed']:
            return {'name': 'sibling_play_denied', **check, 'played': False}
        play_type = 'wrestling' if int(age_days) < 60 else 'chase_play'
        event = {'name': 'cat_sibling_play', 'first': first.name, 'second': second.name, 'relation': check['relation'], 'play_type': play_type, 'age_days': int(age_days), 'day': current_day, 'played': True}
        self._record(first, second, event)
        self._strengthen_relationship(first, second)
        self._strengthen_relationship(second, first)
        return event

    def _record(self, first, second, event):
        for cat, partner in ((first, second), (second, first)):
            cat.sibling_play.play_events += 1
            cat.sibling_play.last_partner = partner.name
            cat.sibling_play.last_play_day = event['day']
            partners = cat.sibling_play.partners
            partners[partner.name] = int(partners.get(partner.name, 0)) + 1
            cat.social_interactions.append(deepcopy(event))
        emit_event = getattr(self.cats_layer, 'emit_event', None)
        if callable(emit_event):
            emit_event(deepcopy(event))

    def _strengthen_relationship(self, cat, other_cat):
        relation = cat.relationships.setdefault(other_cat.name, {'familiarity': 0.0, 'trust': 0.5, 'affiliation': 0.0, 'tension': 0.0, 'shared_scent': 0.0})
        relation['familiarity'] = self._clamp(float(relation.get('familiarity', 0.0)) + 0.04)
        relation['trust'] = self._clamp(float(relation.get('trust', 0.5)) + 0.02)
        relation['affiliation'] = self._clamp(float(relation.get('affiliation', 0.0)) + 0.03)
        relation['tension'] = self._clamp(float(relation.get('tension', 0.0)) - 0.02)
        relation['last_interaction'] = 'sibling_play'

    def _clamp(self, value):
        return max(0.0, min(1.0, value))

    def _require_cat(self, cat):
        if not isinstance(cat, Cat):
            raise TypeError('CatSiblingPlaySystem requires Cat.')
