from dataclasses import dataclass, field

from cats.duplicate_consumption_energy_state import (
    DuplicateConsumptionEnergyState,
)


@dataclass(slots=True, frozen=True)
class DuplicateConsumptionEnergyStoredEvent:
    energy_id: str
    cat: str
    source: str
    day: int
    amount: float
    energy_kind: str
    name: str = field(
        default=(
            "duplicate_consumption_energy_stored"
        ),
        init=False,
    )
    resolved: bool = field(
        default=False,
        init=False,
    )
    resolution: str | None = field(
        default=None,
        init=False,
    )
    energy_conserved: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "energy_id",
            str(self.energy_id),
        )
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )
        object.__setattr__(
            self,
            "source",
            str(self.source),
        )
        object.__setattr__(
            self,
            "day",
            int(self.day),
        )
        object.__setattr__(
            self,
            "amount",
            float(self.amount),
        )
        object.__setattr__(
            self,
            "energy_kind",
            str(self.energy_kind),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "energy_id": self.energy_id,
            "cat": self.cat,
            "source": self.source,
            "day": self.day,
            "amount": self.amount,
            "energy_kind": self.energy_kind,
            "resolved": self.resolved,
            "resolution": self.resolution,
            "energy_conserved": (
                self.energy_conserved
            ),
        }


@dataclass(slots=True, frozen=True)
class DuplicateConsumptionEnergyResolvedEvent:
    energy_id: str
    cat: str
    source: str
    amount: float
    cat_d20_value: int
    resolution: str
    resolved_entity_id: str | None = None
    original_cronenberg_id: str | None = None
    counterpart_id: str | None = None
    fallback_reason: str | None = None
    name: str = field(
        default=(
            "duplicate_consumption_energy_resolved"
        ),
        init=False,
    )
    energy_conserved: bool = field(
        default=True,
        init=False,
    )
    resolved: bool = field(
        default=True,
        init=False,
    )

    def __post_init__(self):
        object.__setattr__(
            self,
            "energy_id",
            str(self.energy_id),
        )
        object.__setattr__(
            self,
            "cat",
            str(self.cat),
        )
        object.__setattr__(
            self,
            "source",
            str(self.source),
        )
        object.__setattr__(
            self,
            "amount",
            float(self.amount),
        )
        object.__setattr__(
            self,
            "cat_d20_value",
            int(self.cat_d20_value),
        )
        object.__setattr__(
            self,
            "resolution",
            str(self.resolution),
        )

    def to_dict(self):
        return {
            "name": self.name,
            "energy_id": self.energy_id,
            "cat": self.cat,
            "source": self.source,
            "amount": self.amount,
            "cat_d20_value": (
                self.cat_d20_value
            ),
            "resolution": self.resolution,
            "resolved_entity_id": (
                self.resolved_entity_id
            ),
            "original_cronenberg_id": (
                self.original_cronenberg_id
            ),
            "counterpart_id": (
                self.counterpart_id
            ),
            "fallback_reason": (
                self.fallback_reason
            ),
            "energy_conserved": (
                self.energy_conserved
            ),
            "resolved": self.resolved,
        }


class DuplicateConsumptionEnergy:

    QUEUE_ATTRIBUTE = (
        "pending_cat_consumption_energy"
    )

    def __init__(
        self,
        universe
    ):
        self.universe = universe
        self.history = []

        if not hasattr(
            self.universe,
            self.QUEUE_ATTRIBUTE
        ):
            setattr(
                self.universe,
                self.QUEUE_ATTRIBUTE,
                []
            )

        self._require_queue()

    @property
    def queue(self):
        return self._require_queue()

    def _require_queue(self):
        queue = getattr(
            self.universe,
            self.QUEUE_ATTRIBUTE
        )

        if not isinstance(
            queue,
            list,
        ):
            raise TypeError(
                "Duplicate consumption energy "
                "queue must be list."
            )

        for item in queue:

            if not isinstance(
                item,
                DuplicateConsumptionEnergyState,
            ):
                raise TypeError(
                    "Duplicate consumption energy "
                    "record must be "
                    "DuplicateConsumptionEnergyState."
                )

        return queue

    def store(
        self,
        cat,
        source,
        day,
        amount=1.0,
        energy_kind=(
            "duplicate_consumption"
        )
    ):
        item_number = len(
            self.queue
        ) + 1

        item = (
            DuplicateConsumptionEnergyState(
                energy_id=(
                    f"cat_consumption_energy_"
                    f"{item_number:04d}"
                ),
                cat=cat.name,
                source=source,
                day=int(day),
                amount=max(
                    0.0,
                    float(amount)
                ),
                energy_kind=energy_kind,
            )
        )

        self.queue.append(
            item
        )

        event = (
            DuplicateConsumptionEnergyStoredEvent(
                energy_id=item.energy_id,
                cat=item.cat,
                source=item.source,
                day=item.day,
                amount=item.amount,
                energy_kind=item.energy_kind,
            )
        )

        self._record(
            event
        )

        return item

    def resolve_next(
        self,
        cat_d20_value
    ):
        pending = next(
            (
                item
                for item in self.queue
                if not item.resolved
            ),
            None
        )

        if pending is None:
            return {
                "name": (
                    "duplicate_consumption_energy_"
                    "resolution_skipped"
                ),
                "reason": "no_pending_energy",
                "cat_d20_value": int(
                    cat_d20_value
                ),
                "resolved": False
            }

        value = int(
            cat_d20_value
        )

        if not 1 <= value <= 20:
            raise ValueError(
                "Cat D20 value must be "
                "between 1 and 20."
            )

        if value <= 10:
            result = (
                self._manifest_cronenberg(
                    pending=pending,
                    reason=(
                        "cat_d20_lower_half"
                    )
                )
            )

        else:
            result = (
                self._create_counterpart_or_fallback(
                    pending=pending
                )
            )

        pending.resolve(
            resolution=result[
                "resolution"
            ],
            cat_d20_value=value,
            resolved_entity_id=(
                result.get(
                    "resolved_entity_id"
                )
            ),
        )

        event = (
            DuplicateConsumptionEnergyResolvedEvent(
                energy_id=pending.energy_id,
                cat=pending.cat,
                source=pending.source,
                amount=pending.amount,
                cat_d20_value=value,
                resolution=result[
                    "resolution"
                ],
                resolved_entity_id=(
                    result.get(
                        "resolved_entity_id"
                    )
                ),
                original_cronenberg_id=(
                    result.get(
                        "original_cronenberg_id"
                    )
                ),
                counterpart_id=result.get(
                    "counterpart_id"
                ),
                fallback_reason=result.get(
                    "fallback_reason"
                ),
            )
        )

        self._record(
            event
        )

        return event.to_dict()

    def _create_counterpart_or_fallback(
        self,
        pending
    ):
        original = next(
            (
                cronenberg
                for cronenberg
                in self.universe.cronenbergs
                if getattr(
                    cronenberg,
                    "is_alive",
                    False
                )
                and cronenberg.quantum_state
                .counterpart_id is None
            ),
            None
        )

        if original is None:
            fallback = (
                self._manifest_cronenberg(
                    pending=pending,
                    reason=(
                        "quantum_twin_target_"
                        "unavailable"
                    )
                )
            )

            fallback[
                "fallback_reason"
            ] = (
                "quantum_twin_target_unavailable"
            )

            return fallback

        counterpart_result = (
            self.universe
            .create_cronenberg_quantum_counterpart(
                original=original,
                source=(
                    "duplicate_consumption_energy"
                )
            )
        )

        counterpart = counterpart_result[
            "counterpart"
        ]

        return {
            "resolution": (
                "cronenberg_quantum_"
                "counterpart_created"
            ),
            "resolved_entity_id": (
                counterpart.id
            ),
            "original_cronenberg_id": (
                original.id
            ),
            "counterpart_id": counterpart.id
        }

    def _manifest_cronenberg(
        self,
        pending,
        reason
    ):
        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Conserved duplicate cat "
                    "consumption energy."
                ),
                source_component=(
                    "duplicate_consumption_energy"
                ),
                source_operation=reason
            )
        )

        return {
            "resolution": (
                "cronenberg_manifested"
            ),
            "resolved_entity_id": (
                cronenberg.id
            )
        }

    def _record(
        self,
        event
    ):
        if not isinstance(
            event,
            (
                DuplicateConsumptionEnergyStoredEvent,
                DuplicateConsumptionEnergyResolvedEvent,
            ),
        ):
            raise TypeError(
                "Duplicate consumption energy "
                "history requires a duplicate "
                "consumption energy event object."
            )

        self.history.append(
            event
        )

        quantum_events = getattr(
            self.universe,
            "quantum_events",
            None
        )

        if quantum_events is not None:
            quantum_events.append(
                event.to_dict()
            )
