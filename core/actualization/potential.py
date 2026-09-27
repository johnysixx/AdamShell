from .potential_state import PotentialState


class Potential:

    def __init__(
        self,
        possibility,
        cycle_id,
        source=None,
        context=None
    ):
        self.possibility = possibility
        self.cycle_id = cycle_id
        self.source = source
        self.context = context or {}

        self.state = PotentialState.OPEN

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if not isinstance(
            state,
            PotentialState,
        ):
            raise TypeError(
                "Potential state must use "
                "PotentialState."
            )

        self._state = state

    @property
    def name(self):
        return self.possibility.name

    @property
    def is_available(self):
        return self.possibility.is_available()

    @property
    def is_open(self):
        return self.state is PotentialState.OPEN

    def mark_actualized(self):
        if not self.is_open:
            return False

        self.state = PotentialState.ACTUALIZED
        return True

    def mark_unrealized(self):
        if not self.is_open:
            return False

        self.state = PotentialState.UNREALIZED
        return True

    @property
    def public_state(self):
        return {
            "name": self.name,
            "cycle_id": self.cycle_id,
            "source": self.source,
            "context": dict(self.context),
            "state": self.state.value,
            "available": self.is_available,
            "mandatory": self.possibility.mandatory,
            "probability": self.possibility.probability
        }
