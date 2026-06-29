from core.word.chronicle import Chronicle
from core.reality.timeline import Timeline
from universe.universe import Universe


class Fork:

    def create(self, base_chronicle: Chronicle, parent_universe: Universe):

        # nový timeline
        timeline = Timeline(parent_id=parent_universe.id)

        # nový universe (klon identity)
        new_universe = Universe(universe_id=f"{parent_universe.id}-fork")

        # REPLAY historie do nové reality
        base_chronicle.replay(new_universe)

        return new_universe, timeline