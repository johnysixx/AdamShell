from .states import (
    TECHNOLOGY_DISCOVERED,
    TECHNOLOGY_ANNOUNCED,
    TECHNOLOGY_INFRASTRUCTURE,
    TECHNOLOGY_ACTIVE,
    TECHNOLOGY_STATES
)


class Technology:

    def __init__(
        self,
        name
    ):
        self.name = name

        self.state = (
            TECHNOLOGY_DISCOVERED
        )

    def set_state(self, state):

        if state not in TECHNOLOGY_STATES:
            raise ValueError(
                f"Unknown technology state: {state}"
            )

        current_index = (
            TECHNOLOGY_STATES.index(
                self.state
            )
        )

        target_index = (
            TECHNOLOGY_STATES.index(
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

        current_index = (
            TECHNOLOGY_STATES.index(
                self.state
            )
        )

        if current_index >= (
            len(TECHNOLOGY_STATES) - 1
        ):
            return False

        self.state = TECHNOLOGY_STATES[
            current_index + 1
        ]

        return True

    @property
    def is_discovered(self):
        return (
            self.state
            == TECHNOLOGY_DISCOVERED
        )

    @property
    def is_announced(self):
        return (
            self.state
            == TECHNOLOGY_ANNOUNCED
        )

    @property
    def has_infrastructure(self):
        return (
            self.state
            == TECHNOLOGY_INFRASTRUCTURE
        )

    @property
    def is_active(self):
        return (
            self.state
            == TECHNOLOGY_ACTIVE
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "state": self.state
        }
