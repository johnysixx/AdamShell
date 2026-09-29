from core.eternal_flame.eternal_flame_objects import (
    EternalFlameHistoryRecord,
    EternalFlameSourceIdea,
)
from core.eternal_flame.eternal_flame_state import (
    EternalFlameState,
)


class EternalFlame:

    def __init__(self):
        self.name = 'eternal_flame'
        self.type = 'cosmic_object'
        self.state = EternalFlameState.UNIGNITED
        self.ignited = False
        self.ignited_at_tick = None
        self.source_idea = None
        self.keeper = None
        self.continuity_intact = False
        self.history = []

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if not isinstance(
            state,
            EternalFlameState,
        ):
            raise TypeError(
                "Eternal flame state must use "
                "EternalFlameState."
            )

        self._state = state

    def ignite(self, source_idea, tick=None, keeper=None):
        if self.ignited:
            record = EternalFlameHistoryRecord.already_burning(
                state=self.state.value,
                tick=tick,
            )
            self.history.append(record)
            return record.to_dict()

        captured_source = EternalFlameSourceIdea.capture(
            source_idea
        )

        self.source_idea = captured_source
        self.ignited = True
        self.state = EternalFlameState.BURNING
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
            'state': self.state.value,
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
