from .cycle_state import ActualizationCycleState


class ActualizationCycle:

    def __init__(self, cycle_id):
        self.cycle_id = cycle_id
        self.state = ActualizationCycleState.OPEN

        self.potentials = []

    def add_potential(self, potential):
        if self.state is not ActualizationCycleState.OPEN:
            return False

        if potential.cycle_id != self.cycle_id:
            raise ValueError(
                "Potential belongs to another cycle."
            )

        self.potentials.append(
            potential
        )

        return True

    def add_potentials(
        self,
        potentials
    ):
        added = []

        for potential in potentials:
            if self.add_potential(
                potential
            ):
                added.append(
                    potential
                )

        return added

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if not isinstance(
            state,
            ActualizationCycleState,
        ):
            raise TypeError(
                "Actualization cycle state must use "
                "ActualizationCycleState."
            )

        self._state = state

    @property
    def open_potentials(self):
        return [
            potential
            for potential in self.potentials
            if potential.is_open
        ]

    @property
    def available_potentials(self):
        return [
            potential
            for potential in self.open_potentials
            if potential.is_available
        ]

    def resolve(self, actualizer=None):
        if self.state is not ActualizationCycleState.OPEN:
            return []

        if actualizer is None:
            from .actualizer import Actualizer
            actualizer = Actualizer()

        selected = actualizer.select(
            self.potentials
        )

        events = actualizer.actualize(
            selected
        )

        for potential in self.open_potentials:
            potential.mark_unrealized()

        self.state = ActualizationCycleState.RESOLVED

        return events

    @property
    def public_state(self):
        return {
            "cycle_id": self.cycle_id,
            "state": self.state.value,
            "potential_count": len(
                self.potentials
            ),
            "open_potential_count": len(
                self.open_potentials
            ),
            "available_potential_count": len(
                self.available_potentials
            ),
            "potentials": [
                potential.public_state
                for potential in self.potentials
            ]
        }
