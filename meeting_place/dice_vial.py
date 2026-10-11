import random
from dataclasses import dataclass, field

from universe.logger import UniverseLogger
from .bar_objects import DiceVialContainer, DiceVialMedium, DiceVialDie


@dataclass(slots=True, frozen=True)
class DiceVialSecretRotationEvent:
    roll: int
    box_created: bool
    quantum_tick_requested: bool

    name: str = field(
        default="dice_vial_secret_rotation",
        init=False,
    )

    def __post_init__(self):
        roll = int(
            self.roll
        )

        if not 1 <= roll <= 20:
            raise ValueError(
                "Dice vial D20 roll must be "
                "between 1 and 20."
            )

        object.__setattr__(
            self,
            "roll",
            roll,
        )

        object.__setattr__(
            self,
            "box_created",
            bool(self.box_created),
        )

        object.__setattr__(
            self,
            "quantum_tick_requested",
            bool(
                self.quantum_tick_requested
            ),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "roll": self.roll,
            "box_created":
                self.box_created,
            "quantum_tick_requested":
                self.quantum_tick_requested,
        }


class DiceVial:

    def __init__(self):
        self.name = "dice_vial"
        self.type = "bar_artifact"
        self.location = "on_bar_counter"

        self.container = DiceVialContainer(
            type="glass_vial",
            state="sealed"
        )

        self.medium = DiceVialMedium(
            type="glowing_oily_liquid",
            state="shimmering"
        )

        self.dice = DiceVialDie(
            type="d20",
            state="floating"
        )

        self.public_state = {
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "container": self.container.to_dict(),
            "medium": self.medium.to_dict(),
            "dice": self.dice.to_dict(),
            "display_state": "displayed",
            "visibility_scope": "inside_bar_only"
        }

        self._secret_roll = None
        self._secret_event = None

        UniverseLogger.boot("DICE VIAL CREATED")
        UniverseLogger.boot(
            "D20 FLOATS IN GLOWING OILY LIQUID"
        )

    def roll(self, rng=None):
        rng = rng or random

        self._secret_roll = rng.randint(
            1,
            20
        )

        box_created = rng.choice(
            [True, False]
        )

        quantum_tick_requested = rng.choice(
            [True, False]
        )

        self._secret_event = (
            DiceVialSecretRotationEvent(
                roll=self._secret_roll,
                box_created=box_created,
                quantum_tick_requested=(
                    quantum_tick_requested
                ),
            )
        )

        return (
            self._secret_event
            .to_dict()
        )

    @property
    def secret_event(self):
        return self._secret_event

    def resolve_missing_universe(self, rng=None):
        event = self.roll(
            rng=rng
        )

        if event["roll"] <= 10:
            return {
                "layer": "multiverse",
                "universe_id": 0,
                "secret_event": event
            }

        return {
            "layer": "quantum_layer",
            "universe_id": 0.5,
            "secret_event": event
        }

    def clear_secret(self):
        self._secret_roll = None
        self._secret_event = None