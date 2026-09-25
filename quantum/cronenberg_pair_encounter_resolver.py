import random
from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType

from universe.logger import UniverseLogger


class _FrozenCronenbergPairList(tuple):
    pass


class _FrozenCronenbergPairSet(frozenset):
    pass


def _freeze_cronenberg_pair_payload(
    value
):
    if isinstance(
        value,
        dict
    ):
        return MappingProxyType(
            {
                key: (
                    _freeze_cronenberg_pair_payload(
                        item
                    )
                )
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list
    ):
        return _FrozenCronenbergPairList(
            _freeze_cronenberg_pair_payload(
                item
            )
            for item in value
        )

    if isinstance(
        value,
        tuple
    ):
        return tuple(
            _freeze_cronenberg_pair_payload(
                item
            )
            for item in value
        )

    if isinstance(
        value,
        set
    ):
        return _FrozenCronenbergPairSet(
            _freeze_cronenberg_pair_payload(
                item
            )
            for item in value
        )

    return value


def _thaw_cronenberg_pair_payload(
    value
):
    if isinstance(
        value,
        MappingProxyType
    ):
        return {
            key: (
                _thaw_cronenberg_pair_payload(
                    item
                )
            )
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        _FrozenCronenbergPairList
    ):
        return [
            _thaw_cronenberg_pair_payload(
                item
            )
            for item in value
        ]

    if isinstance(
        value,
        tuple
    ):
        return tuple(
            _thaw_cronenberg_pair_payload(
                item
            )
            for item in value
        )

    if isinstance(
        value,
        _FrozenCronenbergPairSet
    ):
        return {
            _thaw_cronenberg_pair_payload(
                item
            )
            for item in value
        }

    if isinstance(
        value,
        frozenset
    ):
        return frozenset(
            _thaw_cronenberg_pair_payload(
                item
            )
            for item in value
        )

    return value


@dataclass(
    slots=True,
    frozen=True
)
class CronenbergPairResolvedEffect:

    effect: str
    result: object

    def __post_init__(self):
        object.__setattr__(
            self,
            "effect",
            str(
                self.effect
            ),
        )

        object.__setattr__(
            self,
            "result",
            _freeze_cronenberg_pair_payload(
                self.result
            ),
        )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "effect": self.effect,
            "result": deepcopy(
                _thaw_cronenberg_pair_payload(
                    self.result
                )
            ),
        }


@dataclass(
    slots=True,
    frozen=True
)
class CronenbergPairEncounterResolvedEvent:

    pair_id: str
    participants: tuple[str, ...]
    location: object
    selected_effects: tuple[str, ...]
    resolved_effects: tuple[
        CronenbergPairResolvedEffect,
        ...,
    ]
    skipped_effects: tuple[str, ...]
    universe_tick: object = None

    name: str = field(
        default=(
            "cronenberg_quantum_pair_"
            "encounter_resolved"
        ),
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "pair_id",
            str(
                self.pair_id
            ),
        )

        object.__setattr__(
            self,
            "participants",
            tuple(
                str(item)
                for item
                in self.participants
            ),
        )

        object.__setattr__(
            self,
            "selected_effects",
            tuple(
                str(item)
                for item
                in self.selected_effects
            ),
        )

        resolved = tuple(
            self.resolved_effects
        )

        if not all(
            isinstance(
                item,
                CronenbergPairResolvedEffect,
            )
            for item
            in resolved
        ):
            raise TypeError(
                "Cronenberg pair resolution "
                "history requires "
                "CronenbergPairResolvedEffect "
                "objects."
            )

        object.__setattr__(
            self,
            "resolved_effects",
            resolved,
        )

        object.__setattr__(
            self,
            "skipped_effects",
            tuple(
                str(item)
                for item
                in self.skipped_effects
            ),
        )

    def __deepcopy__(
        self,
        memo
    ):
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "pair_id": self.pair_id,
            "participants": list(
                self.participants
            ),
            "location": deepcopy(
                self.location
            ),
            "selected_effects": list(
                self.selected_effects
            ),
            "resolved_effects": [
                item.to_dict()
                for item
                in self.resolved_effects
            ],
            "skipped_effects": list(
                self.skipped_effects
            ),
            "universe_tick": (
                self.universe_tick
            ),
        }


class CronenbergPairEncounterResolver:

    EFFECTS = (
        "both_survive",
        "quantum_tick",
        "spin_exchange",
        "geometry_shift",
        "property_sum",
        "property_equalization",
        "quantum_merge",
        "quantum_pair_consumption"
    )

    def __init__(self, universe):
        self.name = "cronenberg_pair_encounter_resolver"
        self.universe = universe
        self.history = []

    def resolve(
        self,
        first,
        second,
        encounter_event,
        rng=None
    ):
        rng = rng or random

        if not encounter_event.get("encountered"):
            raise ValueError(
                "Encounter event is not an active pair encounter."
            )

        selected_effects = self._select_effects(
            rng=rng
        )

        selected_effects = self._order_effects(
            selected_effects
        )

        resolved_effects = []
        skipped_effects = []

        for effect_index, effect in enumerate(
            selected_effects
        ):
            if effect == "both_survive":
                result = self._both_survive(
                    first,
                    second
                )

            elif effect == "quantum_tick":
                result = self._quantum_tick()

            elif effect == "spin_exchange":
                result = self._spin_exchange(
                    first,
                    second
                )

            elif effect == "geometry_shift":
                result = self._geometry_shift()

            elif effect == "property_sum":
                result = self._property_sum(
                    first,
                    second
                )

            elif effect == "property_equalization":
                result = self._property_equalization(
                    first,
                    second
                )

            elif effect == "quantum_merge":
                result = (
                    self.universe
                    .merge_cronenberg_quantum_pair(
                        first,
                        second
                    )
                )

            elif effect == "quantum_pair_consumption":
                result = first.consume(
                    second
                )

            else:
                continue

            resolved_effects.append(
                CronenbergPairResolvedEffect(
                    effect=effect,
                    result=result,
                )
            )

            if effect in {
                "quantum_merge",
                "quantum_pair_consumption"
            }:
                skipped_effects.extend(
                    selected_effects[
                        effect_index + 1:
                    ]
                )
                break

        resolution = (
            CronenbergPairEncounterResolvedEvent(
                pair_id=(
                    encounter_event[
                        "pair_id"
                    ]
                ),
                participants=tuple(
                    encounter_event[
                        "participants"
                    ]
                ),
                location=(
                    encounter_event[
                        "location"
                    ]
                ),
                selected_effects=tuple(
                    selected_effects
                ),
                resolved_effects=tuple(
                    resolved_effects
                ),
                skipped_effects=tuple(
                    skipped_effects
                ),
                universe_tick=(
                    encounter_event.get(
                        "universe_tick"
                    )
                ),
            )
        )

        self.record_resolution(
            resolution
        )

        UniverseLogger.event(
            "CRONENBERG QUANTUM PAIR ENCOUNTER "
            f"RESOLVED: {resolution.pair_id} "
            f"EFFECTS={selected_effects}"
        )

        return resolution.to_dict()

    def record_resolution(
        self,
        event
    ):
        if not isinstance(
            event,
            CronenbergPairEncounterResolvedEvent
        ):
            raise TypeError(
                "Cronenberg pair resolution "
                "history requires a "
                "CronenbergPairEncounterResolvedEvent "
                "object."
            )

        self.history.append(
            event
        )

        return event

    def _select_effects(self, rng):
        roll = rng.random()

        if roll < 0.45:
            effect_count = 1
        elif roll < 0.80:
            effect_count = 2
        elif roll < 0.95:
            effect_count = 3
        else:
            effect_count = len(
                self.EFFECTS
            )

        return rng.sample(
            list(self.EFFECTS),
            effect_count
        )

    def _both_survive(
        self,
        first,
        second
    ):
        return {
            "first_alive": first.is_alive,
            "second_alive": second.is_alive,
            "first_id": first.id,
            "second_id": second.id
        }

    def _quantum_tick(self):
        before = self.universe.quantum_state.tick_count

        result = self.universe.tick_quantum()

        after = self.universe.quantum_state.tick_count

        return {
            "before_tick": before,
            "after_tick": after,
            "tick_result": deepcopy(result)
        }

    def _spin_exchange(
        self,
        first,
        second
    ):
        first_before = first.quantum_state.spin

        second_before = second.quantum_state.spin

        first.quantum_state.spin = (
            second_before
        )

        second.quantum_state.spin = (
            first_before
        )

        return {
            "first": {
                "id": first.id,
                "before": first_before,
                "after": first.quantum_state.spin
            },
            "second": {
                "id": second.id,
                "before": second_before,
                "after": second.quantum_state.spin
            }
        }

    def _geometry_shift(self):
        if not hasattr(
            self.universe,
            "quantum_space"
        ):
            self.universe.enable_quantum_layer()

        space = self.universe.quantum_space

        before = {
            "configuration_id": (
                space.configuration_id
            ),
            "reconfiguration_count": (
                space.reconfiguration_count
            )
        }

        space.reconfigure(
            cause="cronenberg_quantum_pair_encounter"
        )

        after = {
            "configuration_id": (
                space.configuration_id
            ),
            "reconfiguration_count": (
                space.reconfiguration_count
            )
        }

        return {
            "before": before,
            "after": after
        }

    def _property_sum(
        self,
        first,
        second
    ):
        before = {
            first.id: {
                "size": first.size,
                "energy": first.energy
            },
            second.id: {
                "size": second.size,
                "energy": second.energy
            }
        }

        combined_size = (
            first.size
            + second.size
        )

        combined_energy = (
            first.energy
            + second.energy
        )

        first.size = combined_size
        second.size = combined_size

        first.energy = combined_energy
        second.energy = combined_energy

        first.juice_value = first.size
        second.juice_value = second.size

        return {
            "mode": "sum_to_both",
            "before": before,
            "combined": {
                "size": combined_size,
                "energy": combined_energy
            },
            "after": {
                first.id: {
                    "size": first.size,
                    "energy": first.energy,
                    "juice_value": first.juice_value
                },
                second.id: {
                    "size": second.size,
                    "energy": second.energy,
                    "juice_value": second.juice_value
                }
            }
        }

    def _property_equalization(
        self,
        first,
        second
    ):
        before = {
            first.id: {
                "size": first.size,
                "energy": first.energy
            },
            second.id: {
                "size": second.size,
                "energy": second.energy
            }
        }

        equal_size = (
            first.size
            + second.size
        ) / 2.0

        equal_energy = (
            first.energy
            + second.energy
        ) / 2.0

        first.size = equal_size
        second.size = equal_size

        first.energy = equal_energy
        second.energy = equal_energy

        first.juice_value = first.size
        second.juice_value = second.size

        return {
            "mode": "equalized_average",
            "before": before,
            "equalized": {
                "size": equal_size,
                "energy": equal_energy
            },
            "after": {
                first.id: {
                    "size": first.size,
                    "energy": first.energy,
                    "juice_value": first.juice_value
                },
                second.id: {
                    "size": second.size,
                    "energy": second.energy,
                    "juice_value": second.juice_value
                }
            }
        }

    def _order_effects(self, effects):
        priority = {
            effect: index
            for index, effect in enumerate(
                self.EFFECTS
            )
        }

        return sorted(
            effects,
            key=lambda effect: priority[
                effect
            ]
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "resolution_count": len(
                self.history
            ),
            "possible_effects": list(
                self.EFFECTS
            )
        }
