from idea_universe.primordial_idea_star_state import (
    PrimordialIdeaStarState,
)
from idea_universe.primordial_stellar_state import (
    PrimordialNebulaRemnant,
)


class PrimordialIdeaStar:

    historical_identity_required = True

    def __init__(self, object_id=None):
        if object_id is not None and (
            not isinstance(object_id, str)
            or not object_id.strip()
        ):
            raise ValueError(
                "Primordial star ID must be "
                "a nonempty string."
            )

        self._id = object_id
        self.name = "primordial_idea_star"
        self.type = "primordial_idea_star"
        self.state = (
            PrimordialIdeaStarState.CREATED
        )

    @property
    def id(self):
        return self._id

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
