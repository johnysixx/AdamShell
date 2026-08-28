from copy import deepcopy

class CatBarGuidanceSystem:

    def __init__(self, invitation_system, meeting_place):
        self.invitation_system = invitation_system
        self.meeting_place = meeting_place
        self.history = []

    def guide(self, cat, human, invitation_id):
        invitation = self.invitation_system.get(invitation_id)
        if invitation is None:
            return self._failed(cat, human, 'unknown_invitation')
        if invitation['cat'] != cat.name:
            return self._failed(cat, human, 'wrong_cat')
        if invitation['human'] != self._name(human):
            return self._failed(cat, human, 'wrong_human')
        if not invitation['understood']:
            return self._failed(cat, human, 'MEOW_not_understood')
        if invitation['used']:
            return self._failed(cat, human, 'invitation_already_used')
        temporary_access = {'source': 'cat_MEOW_invitation', 'inviting_cat': cat.name, 'invitation_id': invitation_id, 'permanent': False}
        self._set(human, 'meow_bar_invitation', temporary_access)
        self._set(human, 'guided_by_cat', cat.name)
        add_entity = getattr(self.meeting_place, 'add_entity', None)
        if not callable(add_entity):
            return self._failed(cat, human, 'meeting_place_cannot_admit')
        escorted_entry = getattr(self.meeting_place, 'add_cat_invited_human', None)
        if callable(escorted_entry):
            admission_result = escorted_entry(human, cat, self.invitation_system)
            if not admission_result.get('entered', False):
                return self._failed(cat, human, admission_result.get('reason', 'escorted_entry_denied'))
        else:
            return self._failed(cat, human, 'meeting_place_has_no_escorted_entry')
        self.invitation_system.mark_used(invitation_id)
        cat.meow_invitations['understood'] += 1
        cat.meow_invitations['guided_to_bar'] += 1
        event = {'name': 'cat_guided_human_to_bar', 'cat': cat.name, 'human': self._name(human), 'invitation_id': invitation_id, 'access': temporary_access, 'admission_result': deepcopy(admission_result), 'guided': True, 'permanent_access': False}
        self.history.append(deepcopy(event))
        cat.meow_invitations['history'].append(deepcopy(event))
        return event

    def _failed(self, cat, human, reason):
        return {'name': 'cat_bar_guidance_failed', 'cat': getattr(cat, 'name', None), 'human': self._name(human), 'reason': reason, 'guided': False}

    def _name(self, entity):
        if isinstance(entity, dict):
            return getattr(entity, 'name', None)
        return getattr(entity, 'name', None)

    def _set(self, entity, key, value):
        if isinstance(entity, dict):
            entity[key] = value
        else:
            setattr(entity, key, value)
