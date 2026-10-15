from idea_universe.primordial_idea_star_state import (
    PrimordialIdeaStarState,
)
from idea_universe.primordial_stellar_state import (
    PrimordialNebulaRemnant,
)


class PrimordialIdeaStar:

    def __init__(self):
        self.name = "primordial_idea_star"
        self.type = "primordial_idea_star"
        self.state = (
            PrimordialIdeaStarState.CREATED
        )

    @property
    def state(self):
        return self._state

    @state.setter
    def state(
        self,
        state,
    ):
        if not isinstance(
            state,
            PrimordialIdeaStarState,
        ):
            raise TypeError(
                "Primordial idea star state must use "
                "PrimordialIdeaStarState."
            )

        self._state = state

    def ignite(self):
        self.state = (
            PrimordialIdeaStarState.BURNING
        )

        return self.state.value

    def explode(self):
        self.state = (
            PrimordialIdeaStarState.EXPLODED
        )

        return PrimordialNebulaRemnant(
            source=self.name,
            elemental_potentials={
                "hydrogen": 1.0,
                "carbon": 1.0,
            },
        )
