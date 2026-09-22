from core.eternal_flame.eternal_flame_objects import (
    EternalFlameHistoryRecord,
    EternalFlameSourceIdea,
)


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
            record = EternalFlameHistoryRecord.already_burning(
                state=self.state,
                tick=tick,
            )
            self.history.append(record)
            return record.to_dict()

        captured_source = EternalFlameSourceIdea.capture(
            source_idea
        )

        self.source_idea = captured_source
        self.ignited = True
        self.state = 'burning'
        self.ignited_at_tick = tick
        self.keeper = keeper
        self.continuity_intact = True

        record = EternalFlameHistoryRecord.ignited(
            source_idea=captured_source,
            keeper=keeper,
            tick=tick,
        )
        self.history.append(record)
        return record.to_dict()

    @property
    def public_state(self):
        return {
            'name': self.name,
            'type': self.type,
            'state': self.state,
            'ignited': self.ignited,
            'ignited_at_tick': self.ignited_at_tick,
            'source_idea': (
                None
                if self.source_idea is None
                else self.source_idea.to_dict()
            ),
            'keeper': self.keeper,
            'continuity_intact': self.continuity_intact,
            'history': [
                record.to_dict()
                for record in self.history
            ],
        }
