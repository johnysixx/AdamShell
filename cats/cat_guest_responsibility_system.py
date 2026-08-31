from copy import deepcopy
from cats.garfield_training_system import GarfieldTrainingSystem
from cats.cat_social_objects import CatGuestIncident

class CatGuestResponsibilitySystem:
    DEFAULT_COOLDOWN_TICKS = 24

    def __init__(self, meeting_place):
        self.meeting_place = meeting_place
        self.garfield = GarfieldTrainingSystem()

    def handle_incident(self, human, cat, invitation_id, category, description=None, cooldown_ticks=None):
        cooldown_ticks = self.DEFAULT_COOLDOWN_TICKS if cooldown_ticks is None else int(cooldown_ticks)
        human_name = self._name(human)
        current_tick = int(getattr(self.meeting_place, 'tick_count', 0))
        suspended_until = current_tick + cooldown_ticks
        if not hasattr(self.meeting_place, 'bar_banned_humans'):
            self.meeting_place.bar_banned_humans = set()
        self.meeting_place.bar_banned_humans.add(human_name)
        self._set(human, 'bar_entry_banned', True)
        self._set(human, 'bar_entry_ban_reason', 'cat_invited_guest_incident')
        cat.meow_invitations.suspended_until_tick = max(int(getattr(cat.meow_invitations, 'suspended_until_tick', 0)), suspended_until)
        cat.meow_invitations.suspension_reason = 'invited_guest_misbehavior'
        incident = CatGuestIncident(**{'name': 'cat_invited_guest_incident', 'human': human_name, 'inviting_cat': cat.name, 'invitation_id': invitation_id, 'category': category, 'description': description, 'human_banned': True, 'cat_MEOW_suspended': True, 'suspended_until_tick': suspended_until, 'cooldown_ticks': cooldown_ticks})
        cat.meow_invitations.history.append(deepcopy(incident))
        training = self.garfield.assign(cat, incident=incident)
        incident.garfield_training = training
        return incident

    def _name(self, entity):
        return getattr(entity, 'name', None)

    def _set(self, entity, key, value):
        setattr(entity, key, value)
