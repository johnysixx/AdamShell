from copy import deepcopy
from uuid import uuid4
from cats.cat import Cat
from cats.cat_human_bond_system import CatHumanBondSystem
from cats.cat_social_objects import CatMeowInvitation

class CatMeowInvitationSystem:

    def __init__(self, cats_layer=None):
        self.cats_layer = cats_layer
        self.bonds = CatHumanBondSystem(cats_layer)
        self.invitations = {}

    def offer(self, cat, human):
        if not isinstance(cat, Cat):
            raise TypeError('MEOW can only be offered by Cat.')
        current_tick = self._current_bar_tick()
        suspended_until = int(cat.meow_invitations.get('suspended_until_tick', 0))
        if current_tick < suspended_until:
            return {'name': 'cat_MEOW_not_offered', 'cat': cat.name, 'human': self._name(human), 'reason': 'cat_MEOW_cooldown', 'current_tick': current_tick, 'suspended_until_tick': suspended_until, 'offered': False}
        if cat.meow_invitations.get('garfield_training_required', False):
            return {'name': 'cat_MEOW_not_offered', 'cat': cat.name, 'human': self._name(human), 'reason': 'garfield_training_required', 'offered': False}
        evaluation = self.bonds.evaluate(cat, human)
        if not evaluation['right_human']:
            return {'name': 'cat_MEOW_not_offered', 'cat': cat.name, 'human': self._name(human), 'reason': 'not_recognized_as_right_human', 'offered': False}
        invitation_id = 'MEOW_' + uuid4().hex[:8]
        invitation = CatMeowInvitation(**{'id': invitation_id, 'name': 'cat_MEOW_invitation', 'cat': cat.name, 'human': self._name(human), 'escort_required': True, 'sound': 'MEOW', 'meaning': 'follow_me', 'offered': True, 'understood': None, 'accepted': False, 'used': False})
        self.invitations[invitation_id] = invitation
        cat.meow_invitations['offered'] += 1
        cat.meow_invitations['history'].append(deepcopy(invitation))
        return deepcopy(invitation)

    def interpret(self, invitation_id, human, understood):
        invitation = self.invitations.get(invitation_id)
        if invitation is None:
            return {'name': 'cat_MEOW_interpretation_failed', 'reason': 'unknown_invitation', 'understood': False}
        if invitation.human != self._name(human):
            return {'name': 'cat_MEOW_interpretation_failed', 'reason': 'wrong_human', 'understood': False}
        invitation.understood = bool(understood)
        invitation.accepted = bool(understood)
        return {'name': 'human_understood_MEOW' if understood else 'human_heard_only_meow', 'invitation_id': invitation_id, 'human': invitation.human, 'understood': bool(understood), 'meaning': 'follow_me' if understood else None}

    def get(self, invitation_id):
        invitation = self.invitations.get(invitation_id)
        if invitation is None:
            return None
        return deepcopy(invitation)

    def mark_used(self, invitation_id):
        invitation = self.invitations[invitation_id]
        invitation.used = True

    def _current_bar_tick(self):
        universe = getattr(self.cats_layer, 'universe', None)
        meeting_place = getattr(universe, 'meeting_place', None)
        return int(getattr(meeting_place, 'tick_count', 0))

    def _name(self, entity):
        return getattr(entity, 'name', None)
