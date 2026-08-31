from core.entity.social_entity import SocialMixin
from universe.logger import UniverseLogger
from .bar_objects import BarOrigin, BouncerPrincipleAttributes, CatEntryPolicy

class Bouncer(SocialMixin):

    def __init__(self, blacklist):
        self.name = 'bouncer'
        self.type = 'bar_guard'
        self.state = 'standing_outside_bar'
        self.origin = BarOrigin(layer='meeting_place', event='bouncer appeared at the bar entrance')
        self.principle_attributes = BouncerPrincipleAttributes(principle='masculine_principle', domain=['boundary', 'protection', 'threshold', 'entry_control'])
        self.position = 'outside_bar'
        self.knows_inside_events = False
        self.allowed_guests = ['god', 'serpent', 'pazuzu', 'classical_probe_debug_entity', 'lilith', 'pazuzu_masculine_principle']
        self.blacklist = blacklist
        self.cat_policy = CatEntryPolicy(cats_are_always_allowed=True, pet_cats_on_entry=True)
        self.cat_meow_history = []
        self.meow_invitation_system = None
        self.cat_invited_guest_history = []
        UniverseLogger.boot('BOUNCER CREATED')
        UniverseLogger.boot('BOUNCER STANDS OUTSIDE THE BAR')

    def can_enter(self, entity):
        entity_name = self._get_entity_name(entity)
        if self._is_cat(entity):
            meow_event = self.receive_cat_meow(entity)
            self.pet_cat(entity)
            allow_event = {'name': 'bouncer_allowed_cat', 'cat': entity_name, 'meow_recognized': meow_event['recognized'], 'allowed': True}
            self.cat_meow_history.append(allow_event)
            UniverseLogger.event(f'BOUNCER ALLOWS CAT: {entity_name}')
            return True
        if self.blacklist.is_banned(entity_name):
            UniverseLogger.event(f'BOUNCER DENIES ENTRY: {entity_name}')
            return False
        if entity_name in self.allowed_guests:
            UniverseLogger.event(f'BOUNCER ALLOWS ENTRY: {entity_name}')
            return True
        UniverseLogger.event(f'BOUNCER DENIES ENTRY: {entity_name}')
        return False

    def eject(self, entity):
        entity_name = self._get_entity_name(entity)
        if entity_name is None:
            return False
        entity.state = 'ejected'
        entity.position = None
        UniverseLogger.event(f'BOUNCER EJECTS: {entity_name}')
        return True

    def register_meow_invitation_system(self, invitation_system):
        self.meow_invitation_system = invitation_system
        return {'name': 'bouncer_registered_MEOW_registry', 'registered': True}

    def can_enter_with_cat(self, human, escorting_cat):
        human_name = self._get_entity_name(human)
        cat_name = self._get_entity_name(escorting_cat)
        claim = self._entity_value(human, 'meow_bar_invitation')
        if not isinstance(claim, dict):
            return {'authorized': False, 'reason': 'no_MEOW_invitation'}
        if claim.get('source') != 'cat_MEOW_invitation':
            return {'authorized': False, 'reason': 'invalid_MEOW_source'}
        if self.meow_invitation_system is None:
            return {'authorized': False, 'reason': 'MEOW_registry_unavailable'}
        invitation_id = claim.get('invitation_id')
        invitation = self.meow_invitation_system.get(invitation_id)
        if invitation is None:
            return {'authorized': False, 'reason': 'unknown_MEOW_invitation'}
        if invitation.human != human_name:
            return {'authorized': False, 'reason': 'MEOW_wrong_human'}
        if invitation.cat != cat_name:
            return {'authorized': False, 'reason': 'MEOW_wrong_cat'}
        if claim.get('inviting_cat') != cat_name:
            return {'authorized': False, 'reason': 'MEOW_claim_cat_mismatch'}
        if not invitation.understood:
            return {'authorized': False, 'reason': 'MEOW_not_understood'}
        if invitation.used:
            return {'authorized': False, 'reason': 'MEOW_already_used'}
        if invitation.escort_required and escorting_cat is None:
            return {'authorized': False, 'reason': 'inviting_cat_not_present'}
        result = {'name': 'bouncer_allows_cat_invited_guest', 'authorized': True, 'human': human_name, 'inviting_cat': cat_name, 'invitation_id': invitation_id, 'guest_type': 'cat_invited_guest'}
        self.cat_invited_guest_history.append(dict(result))
        UniverseLogger.event(f'BOUNCER ALLOWS CAT INVITED GUEST: {human_name} WITH CAT {cat_name}')
        return result

    def _entity_value(self, entity, key, default=None):
        return getattr(entity, key, default)

    def receive_cat_meow(self, cat):
        cat_name = self._get_entity_name(cat)
        knows_meow = self._cat_knows_meow(cat)
        meow_event = {'name': 'cat_meowed_at_bouncer', 'cat': cat_name, 'sound': 'MEOW', 'recognized': knows_meow}
        self.cat_meow_history.append(meow_event)
        UniverseLogger.event(f'CAT MEOWS AT BOUNCER: {cat_name}')
        recognition_event = {'name': 'bouncer_recognized_cat_meow' if knows_meow else 'bouncer_heard_unrecognized_meow', 'cat': cat_name, 'recognized': knows_meow}
        self.cat_meow_history.append(recognition_event)
        if knows_meow:
            UniverseLogger.event(f'BOUNCER RECOGNIZES MEOW: {cat_name}')
        else:
            UniverseLogger.event(f'BOUNCER HEARS ORDINARY CAT SOUND: {cat_name}')
        return recognition_event

    def _cat_knows_meow(self, cat):
        learning = getattr(cat, 'learning', None)
        if not isinstance(learning, dict):
            return False
        meow_knowledge = learning.get('meow_knowledge', {})
        return bool(meow_knowledge.get('learned', False) and meow_knowledge.get('can_speak', False))

    def pet_cat(self, cat, affinity_gain=0.1):
        event = super().pet_cat(cat, affinity_gain=affinity_gain)
        UniverseLogger.event(f"BOUNCER PETS CAT: {getattr(cat, 'name', None)}")
        return event

    def _get_entity_name(self, entity):
        return (
            getattr(entity, 'world_key', None)
            or getattr(entity, 'name', None)
        )

    def _is_cat(self, entity):
        return getattr(entity, 'type', None) == 'cat'
