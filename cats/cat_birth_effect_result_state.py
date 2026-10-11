from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class CatBirthDiceRotationEvent:
    name: str
    cat: str
    identity: str
    d20_rotation: object
    dice_box_rotation: object
    registered_d20_count: int
    bar_dice_count: int
    triggered: bool = field(default=True, init=False)


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


@dataclass(slots=True, frozen=True)
class PazuzuBirthDiceResonanceResult:
    name: str
    triggered: bool
    quantum_d20: object = None
    cat_d20: object = None
    dice_vial: object = None
    dice_box: object = None
    visibility: str | None = None
    tick: int | None = None
    result: str | None = None

    @classmethod
    def from_boundary(cls, payload):
        if not isinstance(payload, dict):
            raise TypeError(
                "Pazuzu birth resonance boundary must be dict."
            )

        return cls(
            name=payload["name"],
            triggered=bool(payload["triggered"]),
            quantum_d20=payload.get("quantum_d20"),
            cat_d20=payload.get("cat_d20"),
            dice_vial=payload.get("dice_vial"),
            dice_box=payload.get("dice_box"),
            visibility=payload.get("visibility"),
            tick=payload.get("tick"),
            result=payload.get("result"),
        )
