from copy import deepcopy

class EternalFlame:

    def __init__(self):
        self.name = 'eternal_flame'
        self.type = 'cosmic_object'
        self.state = 'unignited'
        self.ignited = False
        self.ignited_at_tick = None
        self.source_idea = None
        self.keeper = None
        self.continuity_intact = False
        self.history = []

    def ignite(self, source_idea, tick=None, keeper=None):
        if self.ignited:
            event = {'name': 'eternal_flame_already_burns', 'state': self.state, 'tick': tick}
            self.history.append(event)
            return deepcopy(event)
        if not isinstance(source_idea, dict):
            raise TypeError('Eternal Flame requires an idea source.')
        if getattr(source_idea, 'name', None) != 'eternal_fire':
            raise ValueError('Invalid idea source for Eternal Flame.')
        self.source_idea = {'name': getattr(source_idea, 'name', None), 'type': getattr(source_idea, 'type', None), 'state': getattr(source_idea, 'state', None)}
        self.ignited = True
        self.state = 'burning'
        self.ignited_at_tick = tick
        self.keeper = keeper
        self.continuity_intact = True
        event = {'name': 'eternal_flame_ignited', 'source_idea': deepcopy(self.source_idea), 'keeper': keeper, 'tick': tick}
        self.history.append(event)
        return deepcopy(event)

    @property
    def public_state(self):
        return {'name': self.name, 'type': self.type, 'state': self.state, 'ignited': self.ignited, 'ignited_at_tick': self.ignited_at_tick, 'source_idea': deepcopy(self.source_idea), 'keeper': self.keeper, 'continuity_intact': self.continuity_intact, 'history': deepcopy(self.history)}
