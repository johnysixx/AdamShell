from copy import deepcopy

from universe.logger import UniverseLogger


class PrefysicalFireOrigin:

    # Each attempt converts 5 % of the masculine
    # principle's currently available energy.
    FRICTION_ENERGY_RATIO = 0.05

    # Once wood itself is burning, it is consumed
    # gradually, not instantaneously.
    WOOD_CONSUMPTION_PER_STEP = 0.25

    def __init__(
        self,
        eternal_fire,
        serpent_d20,
        universe=None
    ):
        if not isinstance(
            eternal_fire,
            dict
        ):
            raise TypeError(
                "Prefysical fire requires "
                "the idea eternal_fire."
            )

        if (
            eternal_fire.get(
                "name"
            )
            != "eternal_fire"
        ):
            raise ValueError(
                "Invalid eternal fire idea."
            )

        self.name = (
            "prefysical_fire_origin"
        )

        self.layer = "idea_universe"

        # Day 0 has no physical place.
        self.location = None
        self.physical_time = None
        self.physical_space = None

        self.logical_step = 0

        self.universe = universe
        self.eternal_fire = eternal_fire
        self.serpent_d20 = serpent_d20

        self.participants = [
            "serpent",
            "lilith",
            "pazuzu_masculine_principle"
        ]

        self.temperature_state = "freezing"

        # Serpent finds them.
        # They do not yet belong to the fire.
        self.materials = {
            "wood_sticks": 2,
            "dry_grass": True,
            "found_by": "serpent",
            "handed_to": None
        }

        self.thinking_prompt_given = False

        self.friction_active = False
        self.friction_attempts = 0

        # No energy disappears.
        self.energy_conversion = {
            "masculine_energy_spent_j": 0.0,
            "friction_heat_j": 0.0
        }

        self.fire_significance_understood = False

        self.roles = {
            "fire_guardian": None,
            "fuel_seekers": []
        }

        self.state = "prepared"
        self.history = []

    def begin(
        self,
        universe_tick=None
    ):
        if self.state != "prepared":
            return self._event(
                name=(
                    "prefysical_fire_origin_"
                    "already_started"
                )
            )

        # Serpent gives the sticks to the
        # masculine principle.
        self.materials[
            "handed_to"
        ] = "pazuzu_masculine_principle"

        self.thinking_prompt_given = True
        self.friction_active = True

        self.state = "seeking_warmth"

        event = self._event(
            name=(
                "prefysical_fire_origin_started"
            ),
            details={
                "temperature_state": (
                    self.temperature_state
                ),

                "materials": deepcopy(
                    self.materials
                ),

                "serpent_action": (
                    "finds_wood_and_hands_it_to_"
                    "masculine_principle"
                ),

                "serpent_prompt": (
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
        if (
            self.eternal_fire.get(
                "state"
            )
            == "burning"
        ):
            return self._event(
                name=(
                    "prefysical_eternal_fire_"
                    "already_burns"
                )
            )

        if not self.friction_active:
            raise RuntimeError(
                "Wood friction has not started."
            )

        self.friction_attempts += 1

        # ----------------------------------------------------
        # Pazuzu expends usable idea energy.
        #
        # It is not destroyed:
        #
        # masculine energy
        #       ->
        # friction / heat energy
        # ----------------------------------------------------

        energy_event = (
            self._convert_masculine_energy_to_heat()
        )

        # ----------------------------------------------------
        # Exactly one existing Serpent d20 roll
        # per fire attempt.
        #
        # We do NOT modify the d20 itself.
        # ----------------------------------------------------

        public_roll = (
            self.serpent_d20
            .roll_publicly(
                rng=rng,
                universe_tick=None
            )
        )

        hidden = (
            self.serpent_d20
            .hidden_resolution_for(
                public_roll[
                    "roll_id"
                ]
            )
        )

        attempt_event = self._event(
            name=(
                "prefysical_fire_"
                "ignition_attempt"
            ),
            details={
                "attempt": (
                    self.friction_attempts
                ),

                "public_roll": (
                    deepcopy(
                        public_roll
                    )
                ),

                "friction_active": True,

                "energy_conversion": (
                    deepcopy(
                        energy_event
                    )
                )
            }
        )

        if not hidden[
            "fire_threshold_reached"
        ]:
            return {
                "result": (
                    "fire_not_ignited"
                ),

                "public_roll": deepcopy(
                    public_roll
                ),

                "energy_conversion": (
                    deepcopy(
                        energy_event
                    )
                ),

                "attempt_event": (
                    deepcopy(
                        attempt_event
                    )
                )
            }

        # ----------------------------------------------------
        # SUCCESS:
        # the Eternal Fire NOW comes into existence.
        # ----------------------------------------------------

        self._actualize_eternal_fire(
            public_roll
        )

        ignition_event = self._event(
            name=(
                "prefysical_eternal_fire_ignited"
            ),
            details={
                "public_roll": (
                    deepcopy(
                        public_roll
                    )
                ),

                "ignited_by": (
                    "pazuzu_masculine_principle"
                ),

                "flame_state": "small",

                "fuel": deepcopy(
                    self.eternal_fire[
                        "fuel"
                    ]
                ),

                "heat_energy_j": (
                    self.eternal_fire[
                        "heat_energy_j"
                    ]
                )
            }
        )

        UniverseLogger.event(
            "PREFYSICAL ETERNAL FIRE IGNITED"
        )

        return {
            "result": (
                "prefysical_fire_ignited"
            ),

            "public_roll": deepcopy(
                public_roll
            ),

            "energy_conversion": deepcopy(
                energy_event
            ),

            "ignition_event": deepcopy(
                ignition_event
            )
        }

    def understand_fire_significance(
        self
    ):
        if (
            self.eternal_fire.get(
                "state"
            )
            != "burning"
        ):
            raise RuntimeError(
                "Fire cannot be understood "
                "before it exists."
            )

        if self.fire_significance_understood:
            return self._event(
                name=(
                    "prefysical_fire_significance_"
                    "already_understood"
                ),
                details={
                    "roles": deepcopy(
                        self.roles
                    )
                }
            )

        # ----------------------------------------------------
        # Idea entities understand what just happened.
        # ----------------------------------------------------

        self.fire_significance_understood = True

        self.eternal_fire[
            "meaning"
        ] = {
            "warmth": True,
            "must_be_preserved": True,
            "requires_fuel": True,

            "understood_by": [
                "pazuzu_masculine_principle",
                "lilith",
                "serpent"
            ]
        }

        # ----------------------------------------------------
        # Roles now emerge from understanding the fire.
        # ----------------------------------------------------

        self.roles[
            "fire_guardian"
        ] = (
            "pazuzu_masculine_principle"
        )

        self.roles[
            "fuel_seekers"
        ] = [
            "lilith",
            "serpent"
        ]

        self.eternal_fire[
            "guardian"
        ] = (
            "pazuzu_masculine_principle"
        )

        self.eternal_fire[
            "fuel_seekers"
        ] = [
            "lilith",
            "serpent"
        ]

        self.state = (
            "fire_guarded_fuel_search_active"
        )

        return self._event(
            name=(
                "prefysical_fire_significance_"
                "understood"
            ),
            details={
                "meaning": deepcopy(
                    self.eternal_fire[
                        "meaning"
                    ]
                ),

                "fire_guardian": (
                    "pazuzu_masculine_principle"
                ),

                "fuel_seekers": [
                    "lilith",
                    "serpent"
                ],

                "guardian_action": (
                    "guards_fire"
                ),

                "fuel_seeker_action": (
                    "search_for_something_"
                    "to_feed_fire"
                )
            }
        )

    def advance_fire(
        self
    ):
        if (
            self.eternal_fire.get(
                "state"
            )
            != "burning"
        ):
            raise RuntimeError(
                "Eternal fire is not burning."
            )

        fuel = self.eternal_fire.setdefault(
            "fuel",
            {
                "dry_grass": 0.0,
                "wood_sticks": 0.0
            }
        )

        consumed = {
            "dry_grass": 0.0,
            "wood_sticks": 0.0
        }

        # Tinder goes first.
        if (
            float(
                fuel.get(
                    "dry_grass",
                    0.0
                )
            )
            > 0.0
        ):
            consumed[
                "dry_grass"
            ] = min(
                1.0,
                float(
                    fuel[
                        "dry_grass"
                    ]
                )
            )

            fuel[
                "dry_grass"
            ] -= consumed[
                "dry_grass"
            ]

        # Then the sticks are consumed gradually.
        elif (
            float(
                fuel.get(
                    "wood_sticks",
                    0.0
                )
            )
            > 0.0
        ):
            consumed[
                "wood_sticks"
            ] = min(
                self.WOOD_CONSUMPTION_PER_STEP,
                float(
                    fuel[
                        "wood_sticks"
                    ]
                )
            )

            fuel[
                "wood_sticks"
            ] -= consumed[
                "wood_sticks"
            ]

        remaining = (
            float(
                fuel.get(
                    "dry_grass",
                    0.0
                )
            )
            +
            float(
                fuel.get(
                    "wood_sticks",
                    0.0
                )
            )
        )

        if remaining <= 0.0:
            self.eternal_fire[
                "flame_state"
            ] = "embers"

        elif (
            float(
                fuel.get(
                    "wood_sticks",
                    0.0
                )
            )
            < 1.0
        ):
            self.eternal_fire[
                "flame_state"
            ] = "small_weakening"

        else:
            self.eternal_fire[
                "flame_state"
            ] = "small"

        self.eternal_fire[
            "fuel_consumed_last_step"
        ] = deepcopy(
            consumed
        )

        return self._event(
            name=(
                "prefysical_eternal_fire_"
                "consumes_fuel"
            ),
            details={
                "consumed": deepcopy(
                    consumed
                ),

                "remaining_fuel": deepcopy(
                    fuel
                ),

                "flame_state": (
                    self.eternal_fire[
                        "flame_state"
                    ]
                )
            }
        )

    def _convert_masculine_energy_to_heat(
        self
    ):
        masculine = (
            self._masculine_principle()
        )

        before = float(
            masculine.get(
                "energy_j",
                0.0
            )
        )

        converted = (
            before
            * self.FRICTION_ENERGY_RATIO
        )

        converted = min(
            before,
            max(
                0.0,
                converted
            )
        )

        masculine[
            "energy_j"
        ] = (
            before
            - converted
        )

        self.energy_conversion[
            "masculine_energy_spent_j"
        ] += converted

        self.energy_conversion[
            "friction_heat_j"
        ] += converted

        after = float(
            masculine[
                "energy_j"
            ]
        )

        return {
            "source": (
                "pazuzu_masculine_principle"
            ),

            "source_energy_before_j": before,

            "source_energy_after_j": after,

            "converted_to_friction_heat_j": (
                converted
            ),

            "friction_heat_total_j": (
                self.energy_conversion[
                    "friction_heat_j"
                ]
            ),

            # Explicit conservation invariant.
            "energy_destroyed_j": 0.0
        }

    def _actualize_eternal_fire(
        self,
        public_roll
    ):
        self.eternal_fire[
            "state"
        ] = "burning"

        self.eternal_fire[
            "actualized"
        ] = True

        self.eternal_fire[
            "type"
        ] = "idea_focal_point"

        self.eternal_fire[
            "ignited_by"
        ] = (
            "pazuzu_masculine_principle"
        )

        self.eternal_fire[
            "physical_time"
        ] = None

        self.eternal_fire[
            "physical_location"
        ] = None

        self.eternal_fire[
            "ignited_at_idea_tick"
        ] = None

        self.eternal_fire[
            "ignited_at_logical_step"
        ] = (
            self.logical_step + 1
        )

        # ----------------------------------------------------
        # The initial flame is deliberately small.
        #
        # Dry grass catches.
        # Pazuzu lays the two sticks onto it.
        # ----------------------------------------------------

        self.eternal_fire[
            "flame_state"
        ] = "small"

        self.eternal_fire[
            "fuel"
        ] = {
            "dry_grass": 1.0,

            "wood_sticks": float(
                self.materials[
                    "wood_sticks"
                ]
            ),

            "wood_added_by": (
                "pazuzu_masculine_principle"
            )
        }

        # All friction heat generated by all attempts
        # becomes the initial heat of the fire.
        self.eternal_fire[
            "heat_energy_j"
        ] = (
            self.energy_conversion[
                "friction_heat_j"
            ]
        )

        self.eternal_fire[
            "origin_roll_id"
        ] = public_roll[
            "roll_id"
        ]

        self.friction_active = False
        self.state = "fire_burning"

    def _masculine_principle(
        self
    ):
        if self.universe is None:
            raise RuntimeError(
                "Prefysical fire origin requires "
                "Universe for energy conversion."
            )

        masculine = (
            self.universe.world.get(
                "pazuzu_masculine_principle"
            )
        )

        if not isinstance(
            masculine,
            dict
        ):
            raise RuntimeError(
                "Pazuzu masculine principle "
                "is missing."
            )

        return masculine

    def _event(
        self,
        name,
        universe_tick=None,
        details=None
    ):
        self.logical_step += 1

        event = {
            "name": name,

            "layer": self.layer,

            # Day 0 remains outside physical spacetime.
            "location": None,
            "universe_tick": None,

            "logical_step": (
                self.logical_step
            ),

            "ordering_kind": (
                "logical_precedence"
            ),

            "participants": list(
                self.participants
            ),

            "details": deepcopy(
                details or {}
            )
        }

        self.history.append(
            event
        )

        return deepcopy(
            event
        )

    @property
    def public_state(
        self
    ):
        return {
            "name": self.name,
            "layer": self.layer,
            "location": None,

            "physical_time": None,
            "physical_space": None,

            "logical_step": (
                self.logical_step
            ),

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

            "energy_conversion": deepcopy(
                self.energy_conversion
            ),

            "fire_significance_understood": (
                self.fire_significance_understood
            ),

            "roles": deepcopy(
                self.roles
            ),

            "state": self.state,

            "history": deepcopy(
                self.history
            )
        }
