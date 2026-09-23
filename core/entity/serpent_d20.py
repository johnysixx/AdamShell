import random
import uuid
from copy import deepcopy
from dataclasses import dataclass, field

from quantum.serpent_roll_resolver import SerpentRollResolver


@dataclass(slots=True, frozen=True)
class SerpentD20PublicRollEvent:
    roll_id: str
    roller: str
    die: str
    value: int
    roll_number: int
    universe_tick: int | None = None
    name: str = field(
        default="serpent_d20_rolled",
        init=False,
    )
    visibility: str = field(
        default="public",
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "roll_id",
            str(self.roll_id),
        )
        object.__setattr__(
            self,
            "roller",
            str(self.roller),
        )
        object.__setattr__(
            self,
            "die",
            str(self.die),
        )
        object.__setattr__(
            self,
            "value",
            int(self.value),
        )
        object.__setattr__(
            self,
            "roll_number",
            int(self.roll_number),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "roll_id": self.roll_id,
            "roller": self.roller,
            "die": self.die,
            "value": self.value,
            "roll_number": self.roll_number,
            "universe_tick": self.universe_tick,
            "visibility": self.visibility,
        }


@dataclass(slots=True, frozen=True)
class SerpentResolvedConsequence:
    consequence: str
    result: object

    def __post_init__(self):
        object.__setattr__(
            self,
            "consequence",
            str(self.consequence),
        )
        object.__setattr__(
            self,
            "result",
            deepcopy(self.result),
        )

    def to_dict(self):
        return {
            "consequence": self.consequence,
            "result": deepcopy(
                self.result
            ),
        }


@dataclass(slots=True)
class SerpentD20HiddenResolutionEvent:
    roll_id: str
    value: int
    fire_threshold_reached: bool
    possible_consequences: tuple[str, ...]
    intensity: str
    all_effects_triggered: bool
    resolved_consequences: tuple[
        SerpentResolvedConsequence,
        ...
    ] = ()
    name: str = field(
        default=(
            "serpent_d20_hidden_resolution"
        ),
        init=False,
    )
    visibility: str = field(
        default="universe_only",
        init=False,
    )

    def __post_init__(self):
        self.roll_id = str(
            self.roll_id
        )
        self.value = int(
            self.value
        )
        self.fire_threshold_reached = bool(
            self.fire_threshold_reached
        )
        self.possible_consequences = tuple(
            self.possible_consequences
        )
        self.intensity = str(
            self.intensity
        )
        self.all_effects_triggered = bool(
            self.all_effects_triggered
        )

        self.set_resolved_consequences(
            self.resolved_consequences
        )

    def set_resolved_consequences(
        self,
        resolved_consequences,
    ):
        resolved = tuple(
            resolved_consequences
        )

        if not all(
            isinstance(
                item,
                SerpentResolvedConsequence,
            )
            for item in resolved
        ):
            raise TypeError(
                "Resolved Serpent consequences "
                "must contain "
                "SerpentResolvedConsequence "
                "objects."
            )

        self.resolved_consequences = (
            resolved
        )

        return self

    def to_dict(self):
        return {
            "name": self.name,
            "roll_id": self.roll_id,
            "value": self.value,
            "fire_threshold_reached": (
                self.fire_threshold_reached
            ),
            "possible_consequences": list(
                self.possible_consequences
            ),
            "resolved_consequences": [
                item.to_dict()
                for item
                in self.resolved_consequences
            ],
            "intensity": self.intensity,
            "all_effects_triggered": (
                self.all_effects_triggered
            ),
            "visibility": self.visibility,
        }


class SerpentD20:

    def __init__(self):
        self.name = "serpent_d20"
        self.type = "d20_artifact"
        self.owner = "serpent"
        self.location = "idea_universe"

        self.sides = 20
        self.fire_threshold = 14

        self.roll_count = 0
        self.public_history = []

        self.roll_resolver = SerpentRollResolver()

        # Tento seznam není součástí public_state.
        self._hidden_history = []

    def roll(
        self,
        rng=None,
        universe_tick=None
    ):
        return self.roll_publicly(
            rng=rng,
            universe_tick=universe_tick
        )

    def roll_publicly(
        self,
        rng=None,
        universe_tick=None
    ):
        rng = rng or random

        self.roll_count += 1

        roll_id = (
            f"serpent_roll_"
            f"{uuid.uuid4().hex[:8]}"
        )

        value = rng.randint(
            1,
            self.sides
        )

        public_event = SerpentD20PublicRollEvent(
            roll_id=roll_id,
            roller=self.owner,
            die=self.name,
            value=value,
            roll_number=self.roll_count,
            universe_tick=universe_tick,
        )

        public_snapshot = (
            public_event.to_dict()
        )

        hidden_plan = self.roll_resolver.resolve(
            public_roll=public_snapshot,
            rng=rng
        )

        hidden_event = (
            SerpentD20HiddenResolutionEvent(
                roll_id=roll_id,
                value=value,
                fire_threshold_reached=(
                    value > self.fire_threshold
                ),
                possible_consequences=tuple(
                    hidden_plan[
                        "selected_effects"
                    ]
                ),
                intensity=hidden_plan[
                    "intensity"
                ],
                all_effects_triggered=(
                    hidden_plan[
                        "all_effects_triggered"
                    ]
                ),
            )
        )

        self.record_public_roll(
            public_event
        )

        self.record_hidden_resolution(
            hidden_event
        )

        # Volající dostane pouze veřejnou událost.
        return deepcopy(
            public_snapshot
        )

    def record_public_roll(
        self,
        event,
    ):
        if not isinstance(
            event,
            SerpentD20PublicRollEvent,
        ):
            raise TypeError(
                "Serpent D20 public history "
                "requires a "
                "SerpentD20PublicRollEvent object."
            )

        self.public_history.append(
            event
        )

        return event

    def record_hidden_resolution(
        self,
        event,
    ):
        if not isinstance(
            event,
            SerpentD20HiddenResolutionEvent,
        ):
            raise TypeError(
                "Serpent D20 hidden history "
                "requires a "
                "SerpentD20HiddenResolutionEvent "
                "object."
            )

        self._hidden_history.append(
            event
        )

        return event

    def hidden_resolution_for(self, roll_id):
        event = next(
            (
                item
                for item in self._hidden_history
                if item.roll_id == roll_id
            ),
            None
        )

        if event is None:
            return None

        return event.to_dict()

    @property
    def last_hidden_resolution(self):
        if not self._hidden_history:
            return None

        return (
            self._hidden_history[-1]
            .to_dict()
        )

    def record_resolved_consequences(
        self,
        roll_id,
        resolved_consequences
    ):
        resolved = tuple(
            resolved_consequences
        )

        if not all(
            isinstance(
                item,
                SerpentResolvedConsequence,
            )
            for item in resolved
        ):
            raise TypeError(
                "Resolved Serpent consequences "
                "must contain "
                "SerpentResolvedConsequence "
                "objects."
            )

        for event in self._hidden_history:
            if event.roll_id != roll_id:
                continue

            event.set_resolved_consequences(
                resolved
            )

            return event.to_dict()

        return None

    @property
    def public_state(self):
        return {
            "name": self.name,
            "type": self.type,
            "owner": self.owner,
            "location": self.location,
            "sides": self.sides,
            "roll_count": self.roll_count,
            "public_history": [
                event.to_dict()
                for event in self.public_history
            ]
        }
