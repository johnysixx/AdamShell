from copy import deepcopy

from universe.logger import UniverseLogger


class PrefysicalFireOrigin:

    def __init__(
        self,
        eternal_fire,
        serpent_d20
    ):
        if not isinstance(eternal_fire, dict):
            raise TypeError(
                "Prefysical fire requires "
                "the idea eternal_fire."
            )

        if eternal_fire.get("name") != "eternal_fire":
            raise ValueError(
                "Invalid eternal fire idea."
            )

        self.name = "prefysical_fire_origin"
        self.location = "idea_universe"

        self.eternal_fire = eternal_fire
        self.serpent_d20 = serpent_d20

        self.participants = [
            "serpent",
            "lilith",
            "pazuzu_masculine_principle"
        ]

        self.temperature_state = "freezing"
        self.materials = {
            "wood_sticks": 2,
            "dry_grass": True,
            "found_by": "serpent"
        }

        self.thinking_prompt_given = False
        self.friction_active = False
        self.friction_attempts = 0

        self.state = "prepared"
        self.history = []

    def begin(self, universe_tick=None):
        if self.state != "prepared":
            return self._event(
                name="prefysical_fire_origin_already_started",
                universe_tick=universe_tick
            )

        self.thinking_prompt_given = True
        self.friction_active = True
        self.state = "seeking_warmth"

        event = self._event(
            name="prefysical_fire_origin_started",
            universe_tick=universe_tick,
            details={
                "temperature_state": (
                    self.temperature_state
                ),
                "materials": deepcopy(
                    self.materials
                ),
                "serpent_action": (
                    "asks_masculine_principle_"
                    "to_think_how_to_get_warm"
                ),
                "masculine_principle_action": (
                    "rubs_wood_sticks"
                )
            }
        )

        UniverseLogger.event(
            "PREFYSICAL FIRE ORIGIN STARTED"
        )

        return event

    def attempt_ignition(
        self,
        rng=None,
        universe_tick=None
    ):
        if self.eternal_fire.get("state") == "burning":
            return self._event(
                name="prefysical_eternal_fire_already_burns",
                universe_tick=universe_tick
            )

        if not self.friction_active:
            raise RuntimeError(
                "Wood friction has not started."
            )

        self.friction_attempts += 1

        public_roll = self.serpent_d20.roll_publicly(
            rng=rng,
            universe_tick=universe_tick
        )

        hidden = (
            self.serpent_d20
            .hidden_resolution_for(
                public_roll["roll_id"]
            )
        )

        attempt_event = self._event(
            name="prefysical_fire_ignition_attempt",
            universe_tick=universe_tick,
            details={
                "attempt": self.friction_attempts,
                "public_roll": public_roll,
                "friction_active": True
            }
        )

        if not hidden[
            "fire_threshold_reached"
        ]:
            return {
                "result": "fire_not_ignited",
                "public_roll": deepcopy(
                    public_roll
                ),
                "attempt_event": deepcopy(
                    attempt_event
                )
            }

        self.eternal_fire["state"] = "burning"
        self.eternal_fire["ignited_by"] = (
            "pazuzu_masculine_principle"
        )
        self.eternal_fire["materials"] = (
            deepcopy(self.materials)
        )
        self.eternal_fire[
            "ignited_at_idea_tick"
        ] = universe_tick

        self.friction_active = False
        self.state = "fire_burning"

        ignition_event = self._event(
            name="prefysical_eternal_fire_ignited",
            universe_tick=universe_tick,
            details={
                "public_roll": public_roll,
                "ignited_by": (
                    "pazuzu_masculine_principle"
                ),
                "materials": deepcopy(
                    self.materials
                )
            }
        )

        UniverseLogger.event(
            "PREFYSICAL ETERNAL FIRE IGNITED"
        )

        return {
            "result": "prefysical_fire_ignited",
            "public_roll": deepcopy(
                public_roll
            ),
            "ignition_event": deepcopy(
                ignition_event
            )
        }

    def _event(
        self,
        name,
        universe_tick=None,
        details=None
    ):
        event = {
            "name": name,
            "location": self.location,
            "participants": list(
                self.participants
            ),
            "universe_tick": universe_tick,
            "details": deepcopy(
                details or {}
            )
        }

        self.history.append(event)

        return deepcopy(event)

    @property
    def public_state(self):
        return {
            "name": self.name,
            "location": self.location,
            "participants": list(
                self.participants
            ),
            "temperature_state": (
                self.temperature_state
            ),
            "materials": deepcopy(
                self.materials
            ),
            "thinking_prompt_given": (
                self.thinking_prompt_given
            ),
            "friction_active": (
                self.friction_active
            ),
            "friction_attempts": (
                self.friction_attempts
            ),
            "state": self.state,
            "history": deepcopy(
                self.history
            )
        }
