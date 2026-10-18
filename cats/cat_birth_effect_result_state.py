from dataclasses import dataclass, field

from meeting_place.dice_box import (
    DiceBoxAllRotationEvent,
)


@dataclass(slots=True, frozen=True)
class CatBirthDiceRotationEvent:
    name: str
    cat: str
    identity: str
    d20_rotation: object
    dice_box_rotation: DiceBoxAllRotationEvent
    registered_d20_count: int
    bar_dice_count: int
    triggered: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.dice_box_rotation,
            DiceBoxAllRotationEvent,
        ):
            raise TypeError(
                "Cat birth dice rotation requires "
                "DiceBoxAllRotationEvent."
            )

        if (
            self.bar_dice_count
            != self.dice_box_rotation
            .rotated_count
        ):
            raise ValueError(
                "bar_dice_count must match "
                "DiceBox rotated_count."
            )


@dataclass(slots=True, frozen=True)
class CatBirthNonDiceEffectEvent:
    name: str
    cat: str
    identity: str
    effect_type: str = field(default="non_dice", init=False)
    triggered: bool = field(default=True, init=False)


@dataclass(slots=True, frozen=True)
class QueenElisabethBirthEffectsEvent:
    cat: str
    dice_rotation: CatBirthDiceRotationEvent
    selected_non_dice_effect: str
    non_dice_result: CatBirthNonDiceEffectEvent
    name: str = field(default="queen_elisabeth_birth_effects", init=False)
    identity: str = field(default="queen_elisabeth", init=False)
    triggered: bool = field(default=True, init=False)


@dataclass(slots=True, frozen=True)
class WoodooBirthD20RotationEvent:
    cat: str
    d20_rotation: object
    registered_d20_count: int
    name: str = field(default="woodoo_birth_d20_rotation", init=False)
    identity: str = field(default="woodoo", init=False)
    bar_dice_rotated: bool = field(default=False, init=False)
    triggered: bool = field(default=True, init=False)


@dataclass(slots=True, frozen=True)
class WoodooRebirthQuantumReconfigurationEvent:
    cat: str
    previous_configuration: object
    new_configuration: object
    previous_reconfiguration_count: int
    reconfiguration_count: int
    name: str = field(default="woodoo_rebirth_quantum_reconfiguration", init=False)
    identity: str = field(default="woodoo", init=False)
    next_cat_birth_white: bool = field(default=True, init=False)
    triggered: bool = field(default=True, init=False)


@dataclass(slots=True, frozen=True)
class GarfieldBirthEffectAction:
    name: str
    effect: str
    result: object = None
    pending: bool = False
    triggered: bool = field(default=True, init=False)


@dataclass(slots=True, frozen=True)
class GarfieldBirthEffectCombinationEvent:
    cat: str
    effect_mask: int
    effects: tuple[GarfieldBirthEffectAction, ...]
    force_next_woodoo: bool
    cat_d20_rotated: bool
    quantum_d20_rotated: bool
    name: str = field(default="garfield_birth_effect_combination", init=False)
    identity: str = field(default="garfield", init=False)
    triggered: bool = field(default=True, init=False)

    @property
    def effect_names(self):
        return tuple(effect.effect for effect in self.effects)

    @property
    def effect_count(self):
        return len(self.effects)
