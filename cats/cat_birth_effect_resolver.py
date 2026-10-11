import random

from cats.cat_birth_effect_result_state import (
    CatBirthDiceRotationEvent,
    CatBirthNonDiceEffectEvent,
    GarfieldBirthEffectAction,
    GarfieldBirthEffectCombinationEvent,
    QueenElisabethBirthEffectsEvent,
    PazuzuBirthDiceResonanceResult,
    WoodooBirthD20RotationEvent,
    WoodooRebirthQuantumReconfigurationEvent,
)


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
                PazuzuBirthDiceResonanceResult
                .from_boundary(
                    self.meeting_place
                    .trigger_pazuzu_birth_dice_resonance(
                        rng=rng
                    )
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

            result = QueenElisabethBirthEffectsEvent(
                cat=cat_name,
                dice_rotation=rotation,
                selected_non_dice_effect=(
                    selected_effect
                ),
                non_dice_result=(
                    non_dice_result
                ),
            )

            self._record(
                result,
                emit_to_meeting_place=True
            )

        elif identity == "garfield":
            result = self._execute_garfield_effects(
                cat_name=cat_name,
                rng=rng
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

            result = WoodooBirthD20RotationEvent(
                cat=cat_name,
                d20_rotation=d20_rotation,
                registered_d20_count=(
                    d20_rotation[
                        "rotated_count"
                    ]
                ),
            )

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

            result = WoodooRebirthQuantumReconfigurationEvent(
                cat=cat_name,
                previous_configuration=(
                    previous_configuration
                ),
                new_configuration=(
                    quantum_space.configuration_id
                ),
                previous_reconfiguration_count=(
                    previous_reconfiguration_count
                ),
                reconfiguration_count=(
                    quantum_space
                    .reconfiguration_count
                ),
            )

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

    def _execute_garfield_effects(
        self,
        cat_name,
        rng=None
    ):
        rng = rng or random

        # 1–7 představuje všech sedm neprázdných
        # kombinací tří možných efektů.
        effect_mask = rng.randint(
            1,
            7
        )

        force_next_woodoo = bool(
            effect_mask & 1
        )

        rotate_cat_d20 = bool(
            effect_mask & 2
        )

        rotate_quantum_d20 = bool(
            effect_mask & 4
        )

        effects = []

        if force_next_woodoo:
            self.universe.force_next_woodoo_birth = True

            effects.append(
                GarfieldBirthEffectAction(
                    name=(
                        "garfield_forces_next_"
                        "woodoo_birth"
                    ),
                    effect="force_next_woodoo",
                    pending=True,
                )
            )

        if rotate_cat_d20:
            cat_d20_result = (
                self.meeting_place
                .turn_cat_d20_in_box(
                    rng=rng
                )
            )

            effects.append(
                GarfieldBirthEffectAction(
                    name=(
                        "garfield_rotates_cat_d20"
                    ),
                    effect="rotate_cat_d20",
                    result=cat_d20_result,
                )
            )

        if rotate_quantum_d20:
            quantum_d20_result = (
                self.universe
                .quantum_die
                .roll(
                    rng=rng
                )
            )

            effects.append(
                GarfieldBirthEffectAction(
                    name=(
                        "garfield_rotates_quantum_d20"
                    ),
                    effect="rotate_quantum_d20",
                    result=quantum_d20_result,
                )
            )

        result = GarfieldBirthEffectCombinationEvent(
            cat=cat_name,
            effect_mask=effect_mask,
            effects=tuple(effects),
            force_next_woodoo=(
                force_next_woodoo
            ),
            cat_d20_rotated=(
                rotate_cat_d20
            ),
            quantum_d20_rotated=(
                rotate_quantum_d20
            ),
        )

        self._record(
            result,
            emit_to_meeting_place=True
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

        result = CatBirthDiceRotationEvent(
            name=event_name,
            cat=cat_name,
            identity=identity,
            d20_rotation=d20_rotation,
            dice_box_rotation=(
                dice_box_rotation
            ),
            registered_d20_count=(
                d20_rotation[
                    "rotated_count"
                ]
            ),
            bar_dice_count=(
                dice_box_rotation[
                    "rotated_count"
                ]
            ),
        )

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
        result = CatBirthNonDiceEffectEvent(
            name=effect_name,
            cat=cat_name,
            identity=identity,
        )

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