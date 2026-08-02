import random


class CatBirthEffectResolver:

    NON_DICE_EFFECTS = (
        "woodoo_birth_chaos",
        "woodoo_rebirth_chaos"
    )

    def __init__(
        self,
        universe,
        meeting_place
    ):
        self.universe = universe
        self.meeting_place = meeting_place
        self.history = []

    def execute(
        self,
        identity,
        cat_name,
        rng=None,
        special_birth_event=None
    ):
        if identity == "pazuzu":
            result = (
                self.meeting_place
                .trigger_pazuzu_birth_dice_resonance(
                    rng=rng
                )
            )

        elif identity == "gib":
            result = self._rotate_all_dice(
                cat_name=cat_name,
                identity="gib",
                event_name=(
                    "gib_birth_global_resonance"
                ),
                rng=rng,
                emit_to_meeting_place=False
            )

        elif identity == "mia":
            result = self._rotate_all_dice(
                cat_name=cat_name,
                identity="mia",
                event_name=(
                    "mia_birth_global_rotation"
                ),
                rng=rng,
                emit_to_meeting_place=True
            )

        elif identity == "queen_elisabeth":
            rotation = self._rotate_all_dice(
                cat_name=cat_name,
                identity="queen_elisabeth",
                event_name=(
                    "queen_elisabeth_birth_"
                    "global_rotation"
                ),
                rng=rng,
                emit_to_meeting_place=True
            )

            selected_effect = (
                self._select_non_dice_effect(
                    rng=rng
                )
            )

            non_dice_result = (
                self._emit_non_dice_effect(
                    effect_name=selected_effect,
                    cat_name=cat_name,
                    identity="queen_elisabeth"
                )
            )

            result = {
                "name": (
                    "queen_elisabeth_birth_effects"
                ),
                "cat": cat_name,
                "identity": "queen_elisabeth",
                "dice_rotation": rotation,
                "selected_non_dice_effect": (
                    selected_effect
                ),
                "non_dice_result": (
                    non_dice_result
                ),
                "triggered": True
            }

            self._record(
                result,
                emit_to_meeting_place=True
            )

        elif identity == "garfield":
            effects = [
                self._emit_non_dice_effect(
                    effect_name=effect_name,
                    cat_name=cat_name,
                    identity="garfield"
                )
                for effect_name
                in self.NON_DICE_EFFECTS
            ]

            result = {
                "name": (
                    "garfield_birth_all_"
                    "non_dice_effects"
                ),
                "cat": cat_name,
                "identity": "garfield",
                "effects": effects,
                "effect_names": list(
                    self.NON_DICE_EFFECTS
                ),
                "dice_rotated": False,
                "triggered": True
            }

            self._record(
                result,
                emit_to_meeting_place=True
            )

        elif (
            identity == "woodoo"
            and special_birth_event
            == "woodoo_birth_chaos"
        ):
            d20_rotation = (
                self.universe
                .d20_registry
                .rotate_all(
                    rng=rng
                )
            )

            result = {
                "name": (
                    "woodoo_birth_d20_rotation"
                ),
                "cat": cat_name,
                "identity": "woodoo",
                "d20_rotation": d20_rotation,
                "registered_d20_count": (
                    d20_rotation[
                        "rotated_count"
                    ]
                ),
                "bar_dice_rotated": False,
                "triggered": True
            }

            self._record(
                result,
                emit_to_meeting_place=True
            )

        elif (
            identity == "woodoo"
            and special_birth_event
            == "woodoo_rebirth_chaos"
        ):
            quantum_space = (
                self.universe
                .quantum_space
            )

            previous_configuration = (
                quantum_space.configuration_id
            )

            previous_reconfiguration_count = (
                quantum_space
                .reconfiguration_count
            )

            compatible_rng = (
                rng
                if (
                    rng is not None
                    and hasattr(rng, "randint")
                    and hasattr(rng, "uniform")
                    and hasattr(rng, "choice")
                )
                else None
            )

            quantum_space.reconfigure(
                cause="woodoo_rebirth",
                rng=compatible_rng
            )

            self.universe.next_cat_birth_white = True

            result = {
                "name": (
                    "woodoo_rebirth_quantum_"
                    "reconfiguration"
                ),
                "cat": cat_name,
                "identity": "woodoo",
                "previous_configuration": (
                    previous_configuration
                ),
                "new_configuration": (
                    quantum_space.configuration_id
                ),
                "previous_reconfiguration_count": (
                    previous_reconfiguration_count
                ),
                "reconfiguration_count": (
                    quantum_space
                    .reconfiguration_count
                ),
                "next_cat_birth_white": True,
                "triggered": True
            }

            self._record(
                result,
                emit_to_meeting_place=True
            )

        else:
            return None

        self.history.append(
            result
        )

        return result

    def _rotate_all_dice(
        self,
        cat_name,
        identity,
        event_name,
        rng=None,
        emit_to_meeting_place=False
    ):
        d20_rotation = (
            self.universe
            .d20_registry
            .rotate_all(
                rng=rng
            )
        )

        dice_box_rotation = (
            self.meeting_place
            .dice_box
            .rotate_all_dice(
                rng=rng
            )
        )

        result = {
            "name": event_name,
            "cat": cat_name,
            "identity": identity,
            "d20_rotation": d20_rotation,
            "dice_box_rotation": (
                dice_box_rotation
            ),
            "registered_d20_count": (
                d20_rotation[
                    "rotated_count"
                ]
            ),
            "bar_dice_count": (
                dice_box_rotation[
                    "rotated_count"
                ]
            ),
            "triggered": True
        }

        self._record(
            result,
            emit_to_meeting_place=(
                emit_to_meeting_place
            )
        )

        return result

    def _emit_non_dice_effect(
        self,
        effect_name,
        cat_name,
        identity
    ):
        result = {
            "name": effect_name,
            "cat": cat_name,
            "identity": identity,
            "effect_type": "non_dice",
            "triggered": True
        }

        self._record(
            result,
            emit_to_meeting_place=True
        )

        return result

    def _record(
        self,
        event,
        emit_to_meeting_place=False
    ):
        self.universe.quantum_events.append(
            event
        )

        if emit_to_meeting_place:
            self.meeting_place.emit_event(
                event
            )

    def _select_non_dice_effect(
        self,
        rng=None
    ):
        rng = rng or random

        if hasattr(
            rng,
            "choice"
        ):
            return rng.choice(
                list(
                    self.NON_DICE_EFFECTS
                )
            )

        return random.choice(
            list(
                self.NON_DICE_EFFECTS
            )
        )