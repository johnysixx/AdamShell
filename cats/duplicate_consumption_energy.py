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

    @property
    def queue(self):
        return getattr(
            self.universe,
            self.QUEUE_ATTRIBUTE
        )

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

        item = {
            "name": (
                "duplicate_consumption_energy_stored"
            ),
            "energy_id": (
                f"cat_consumption_energy_"
                f"{item_number:04d}"
            ),
            "cat": cat.name,
            "source": source,
            "day": int(day),
            "amount": max(
                0.0,
                float(amount)
            ),
            "energy_kind": energy_kind,
            "resolved": False,
            "resolution": None,
            "energy_conserved": True
        }

        self.queue.append(
            item
        )

        self._record(
            item
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
                if not item.get(
                    "resolved",
                    False
                )
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

        pending.update({
            "resolved": True,
            "resolution": result[
                "resolution"
            ],
            "cat_d20_value": value,
            "resolved_entity_id": (
                result.get(
                    "resolved_entity_id"
                )
            )
        })

        event = {
            "name": (
                "duplicate_consumption_energy_resolved"
            ),
            "energy_id": pending[
                "energy_id"
            ],
            "cat": pending["cat"],
            "source": pending["source"],
            "amount": pending["amount"],
            "cat_d20_value": value,
            "resolution": result[
                "resolution"
            ],
            "resolved_entity_id": (
                result.get(
                    "resolved_entity_id"
                )
            ),
            "original_cronenberg_id": (
                result.get(
                    "original_cronenberg_id"
                )
            ),
            "counterpart_id": result.get(
                "counterpart_id"
            ),
            "fallback_reason": result.get(
                "fallback_reason"
            ),
            "energy_conserved": True,
            "resolved": True
        }

        self._record(
            event
        )

        return event

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
                and cronenberg.quantum_state.get(
                    "counterpart_id"
                ) is None
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
                dict(event)
            )