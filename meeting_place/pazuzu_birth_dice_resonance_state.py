from dataclasses import dataclass, field

from cats.duplicate_consumption_energy import (
    DuplicateConsumptionEnergyResolvedEvent,
    DuplicateConsumptionEnergyResolutionSkippedResult,
)
from core.entity.quantum_die import (
    QuantumDieRollEvent,
)
from meeting_place.bar_objects import (
    CatD20TurnEvent,
)
from meeting_place.cat_d20_turn_state import (
    CatD20ValueInterpretation,
)
from meeting_place.dice_box import (
    DiceBoxRotationEvent,
)
from meeting_place.dice_vial import (
    DiceVialSecretRotationEvent,
)
from quantum.quantum_die_resolver import (
    QuantumDieResolutionEvent,
)


@dataclass(slots=True, frozen=True)
class PazuzuCatD20ResonanceTurn:
    turn: CatD20TurnEvent
    duplicate_consumption_energy: (
        DuplicateConsumptionEnergyResolvedEvent
        | DuplicateConsumptionEnergyResolutionSkippedResult
    )

    def __post_init__(self):
        if not isinstance(
            self.turn,
            CatD20TurnEvent,
        ):
            raise TypeError(
                "Pazuzu resonance CatD20 turn "
                "must use CatD20TurnEvent."
            )

        if not isinstance(
            self.duplicate_consumption_energy,
            (
                DuplicateConsumptionEnergyResolvedEvent,
                DuplicateConsumptionEnergyResolutionSkippedResult,
            ),
        ):
            raise TypeError(
                "Pazuzu resonance energy result "
                "must use a duplicate consumption "
                "energy result object."
            )

    @property
    def interpretation(self):
        return CatD20ValueInterpretation(
            value=self.turn.value
        )

    @property
    def meaning(self):
        return (
            self.interpretation
            .meaning
        )

    def to_dict(self):
        result = (
            self.turn.to_dict()
        )

        result["interpretation"] = (
            self.interpretation
            .to_dict()
        )

        # Preserve the existing public boundary contract:
        # this field has already returned the typed energy
        # result object rather than a nested serialized dict.
        result[
            "duplicate_consumption_energy"
        ] = (
            self.duplicate_consumption_energy
        )

        return result


@dataclass(slots=True, frozen=True)
class PazuzuBirthDiceResonanceEvent:
    quantum_d20: QuantumDieRollEvent
    quantum_resolution: (
        QuantumDieResolutionEvent
        | None
    )
    cat_d20: PazuzuCatD20ResonanceTurn
    dice_vial: DiceVialSecretRotationEvent
    dice_box: DiceBoxRotationEvent
    tick: int = 0

    name: str = field(
        default="pazuzu_birth_dice_resonance",
        init=False,
    )

    triggered: bool = field(
        default=True,
        init=False,
    )

    visibility: str = field(
        default="secret_multiverse_event",
        init=False,
    )

    def __post_init__(self):
        if not isinstance(
            self.quantum_d20,
            QuantumDieRollEvent,
        ):
            raise TypeError(
                "Pazuzu resonance quantum D20 "
                "must use QuantumDieRollEvent."
            )

        if (
            self.quantum_resolution is not None
            and not isinstance(
                self.quantum_resolution,
                QuantumDieResolutionEvent,
            )
        ):
            raise TypeError(
                "Pazuzu resonance quantum resolution "
                "must use QuantumDieResolutionEvent."
            )

        if not isinstance(
            self.cat_d20,
            PazuzuCatD20ResonanceTurn,
        ):
            raise TypeError(
                "Pazuzu resonance CatD20 result "
                "must use PazuzuCatD20ResonanceTurn."
            )

        if not isinstance(
            self.dice_vial,
            DiceVialSecretRotationEvent,
        ):
            raise TypeError(
                "Pazuzu resonance dice vial result "
                "must use DiceVialSecretRotationEvent."
            )

        if not isinstance(
            self.dice_box,
            DiceBoxRotationEvent,
        ):
            raise TypeError(
                "Pazuzu resonance dice box result "
                "must use DiceBoxRotationEvent."
            )

        object.__setattr__(
            self,
            "tick",
            int(self.tick),
        )

    def to_dict(self):
        quantum_d20 = (
            self.quantum_d20
            .to_dict()
        )

        if self.quantum_resolution is not None:
            quantum_d20[
                "resolution"
            ] = (
                self.quantum_resolution
                .to_dict()
            )

        return {
            "name": self.name,
            "quantum_d20":
                quantum_d20,
            "cat_d20":
                self.cat_d20.to_dict(),
            "dice_vial":
                self.dice_vial.to_dict(),
            "dice_box":
                self.dice_box.to_dict(),
            "triggered":
                self.triggered,
            "visibility":
                self.visibility,
            "tick": self.tick,
        }
