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

        hidden_event = {
            "name": "serpent_d20_hidden_resolution",
            "roll_id": roll_id,
            "value": value,
            "fire_threshold_reached": (
                value > self.fire_threshold
            ),
            "possible_consequences": list(
                hidden_plan["selected_effects"]
            ),
            "resolved_consequences": [],
            "intensity": hidden_plan["intensity"],
            "all_effects_triggered": (
                hidden_plan[
                    "all_effects_triggered"
                ]
            ),
            "visibility": "universe_only"
        }

        self.record_public_roll(
            public_event
        )

        self._hidden_history.append(
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

    def hidden_resolution_for(self, roll_id):
        event = next(
            (
                item
                for item in self._hidden_history
                if item["roll_id"] == roll_id
            ),
            None
        )

        return deepcopy(event)

    @property
    def last_hidden_resolution(self):
        if not self._hidden_history:
            return None

        return deepcopy(
            self._hidden_history[-1]
        )

    def record_resolved_consequences(
        self,
        roll_id,
        resolved_consequences
    ):
        for event in self._hidden_history:
            if event["roll_id"] != roll_id:
                continue

            event["resolved_consequences"] = deepcopy(
                resolved_consequences
            )

            return deepcopy(event)

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
