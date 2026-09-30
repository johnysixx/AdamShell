from .technology_state import TechnologyState


class Technology:

    def __init__(
        self,
        name
    ):
        self.name = name

        self.state = (
            TechnologyState.DISCOVERED
        )

    @property
    def state(self):
        return self._state

    @state.setter
    def state(
        self,
        state
    ):
        if not isinstance(
            state,
            TechnologyState,
        ):
            raise TypeError(
                "Technology state must use "
                "TechnologyState."
            )

        self._state = state

    def set_state(
        self,
        state
    ):
        if not isinstance(
            state,
            TechnologyState,
        ):
            raise TypeError(
                "Technology state must use "
                "TechnologyState."
            )

        states = tuple(
            TechnologyState
        )

        current_index = (
            states.index(
                self.state
            )
        )

        target_index = (
            states.index(
                state
            )
        )

        if target_index == current_index:
            return False

        if target_index != current_index + 1:
            raise ValueError(
                "Technology state transition must "
                "advance by exactly one phase."
            )

        self.state = state

        return True

    def advance(self):

        states = tuple(
            TechnologyState
        )

        current_index = (
            states.index(
                self.state
            )
        )

        if current_index >= (
            len(states) - 1
        ):
            return False

        self.state = states[
            current_index + 1
        ]

        return True

    @property
    def is_discovered(self):
        return (
            self.state
            is TechnologyState.DISCOVERED
        )

    @property
    def is_announced(self):
        return (
            self.state
            is TechnologyState.ANNOUNCED
        )

    @property
    def has_infrastructure(self):
        return (
            self.state
            is TechnologyState.INFRASTRUCTURE
        )

    @property
    def is_active(self):
        return (
            self.state
            is TechnologyState.ACTIVE
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "state": self.state.value
        }
