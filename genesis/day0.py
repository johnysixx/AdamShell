from copy import deepcopy

from genesis.day0_state import GenesisDay0State


class GenesisDay0:
    """
    First canonical sequence inside Idea Universe.

    There is no physical time and no physical space.
    Events are ordered only by logical precedence.
    """

    REQUIRED_PRINCIPLES = (
        "serpent",
        "lilith",
        "pazuzu_masculine_principle"
    )

    def __init__(
        self,
        universe,
        idea_entities
    ):
        self.universe = universe
        self.idea_entities = (
            idea_entities
        )

        self.fire_origin = (
            idea_entities
            .prefysical_fire_origin
        )

        self.genesis_day0_state = GenesisDay0State()
        self.state = self.genesis_day0_state

    @property
    def status(self):
        return self.genesis_day0_state.status

    @status.setter
    def status(self, value):
        self.genesis_day0_state.status = value

    @property
    def history(self):
        return self.genesis_day0_state.history

    def verify_principles(
        self
    ):
        missing = [
            key
            for key
            in self.REQUIRED_PRINCIPLES
            if key not in self.universe.world
        ]

        if missing:
            raise RuntimeError(
                "Genesis Day 0 requires "
                "existing idea principles: "
                f"{missing}"
            )

        event = {
            "name": (
                "genesis_day0_principles_present"
            ),

            "participants": list(
                self.REQUIRED_PRINCIPLES
            ),

            "physical_time": None,
            "physical_space": None,

            "ordering_kind": (
                "logical_precedence"
            )
        }

        self.history.append(
            event
        )

        self.status = (
            "ready_for_fire_origin"
        )

        return deepcopy(
            event
        )

    def begin_fire_origin(
        self
    ):
        if (
            self.status
            == "principles_required"
        ):
            self.verify_principles()

        event = self.fire_origin.begin(
            universe_tick=None
        )

        self.history.append(
            deepcopy(
                event
            )
        )

        self.status = (
            "seeking_warmth"
        )

        return deepcopy(
            event
        )

    def attempt_fire(
        self,
        rng=None
    ):
        if (
            self.status
            == "principles_required"
        ):
            self.verify_principles()

        if (
            self.fire_origin.state
            == "prepared"
        ):
            self.begin_fire_origin()

        result = (
            self.fire_origin
            .attempt_ignition(
                rng=rng,
                universe_tick=None
            )
        )

        self.history.append(
            deepcopy(
                result
            )
        )

        if (
            result["result"]
            == "prefysical_fire_ignited"
        ):
            self.status = (
                "eternal_fire_exists"
            )

        else:
            self.status = (
                "seeking_warmth"
            )

        return deepcopy(
            result
        )

    def understand_fire(
        self
    ):
        if not self.eternal_fire_exists:
            raise RuntimeError(
                "The Eternal Fire does not yet exist."
            )

        result = (
            self.fire_origin
            .understand_fire_significance()
        )

        self.history.append(
            deepcopy(
                result
            )
        )

        self.status = (
            "fire_guarded_fuel_search_active"
        )

        return deepcopy(
            result
        )

    def advance_fire(
        self
    ):
        if not self.eternal_fire_exists:
            raise RuntimeError(
                "The Eternal Fire does not yet exist."
            )

        result = (
            self.fire_origin
            .advance_fire()
        )

        self.history.append(
            deepcopy(
                result
            )
        )

        return deepcopy(
            result
        )

    @property
    def eternal_fire_exists(
        self
    ):
        fire = (
            self.idea_entities
            .eternal_fire
        )

        return bool(
            fire.actualized
            and fire.state == "burning"
        )

    @property
    def public_state(
        self
    ):
        return {
            "name": self.genesis_day0_state.name,
            "state": self.status,

            "physical_time_exists": (
                self.genesis_day0_state.physical_time_exists
            ),
            "physical_space_exists": (
                self.genesis_day0_state.physical_space_exists
            ),

            "eternal_fire_exists": (
                self.eternal_fire_exists
            ),

            "history": deepcopy(
                self.history
            ),

            "genesis_day0_state": (
                self.genesis_day0_state.to_dict()
            )
        }
