from copy import deepcopy

from universe.logger import UniverseLogger


class QuantumDieResolver:

    def __init__(self, universe):
        self.name = "quantum_die_resolver"
        self.universe = universe
        self.history = []

    def resolve(
        self,
        roll_event,
        source="quantum_die"
    ):
        value = int(
            roll_event["value"]
        )

        if value < 1 or value > 20:
            raise ValueError(
                "Quantum d20 result must be between 1 and 20."
            )

        if value == 20:
            resolution = self._resolve_twenty(
                source=source
            )
        else:
            resolution = self._resolve_standard(
                source=source
            )

        event = {
            "name": "quantum_die_resolved",
            "die": roll_event.get(
                "die",
                "quantum_d20"
            ),
            "value": value,
            "roll_number": roll_event.get(
                "roll_number"
            ),
            "source": source,
            "resolution": resolution,
            "visibility": "universe_only"
        }

        self.history.append(
            event
        )

        UniverseLogger.event(
            "QUANTUM DIE RESOLVED "
            f"ROLL={value} "
            f"RESULT={resolution['result']}"
        )

        return deepcopy(event)

    def _resolve_standard(self, source):
        cronenberg = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Quantum d20 manifestation."
                ),
                source_component="quantum_die",
                source_operation=source
            )
        )

        return {
            "result": "single_cronenberg_manifested",
            "cronenberg_id": cronenberg.id
        }

    def _resolve_twenty(self, source):
        candidate = self._find_counterpart_candidate()

        if candidate is not None:
            result = (
                self.universe
                .create_cronenberg_quantum_counterpart(
                    original=candidate,
                    source=source
                )
            )

            counterpart = result[
                "counterpart"
            ]

            return {
                "result": (
                    "existing_cronenberg_counterpart_manifested"
                ),
                "original_id": candidate.id,
                "counterpart_id": counterpart.id,
                "pair_id": result["pair_id"]
            }

        original = (
            self.universe
            .create_cronenberg_from_quantum_error(
                error=RuntimeError(
                    "Quantum d20 critical pair manifestation."
                ),
                source_component="quantum_die",
                source_operation=source
            )
        )

        pair_result = (
            self.universe
            .create_cronenberg_quantum_counterpart(
                original=original,
                source=source
            )
        )

        counterpart = pair_result[
            "counterpart"
        ]

        return {
            "result": "new_cronenberg_pair_manifested",
            "original_id": original.id,
            "counterpart_id": counterpart.id,
            "pair_id": pair_result["pair_id"]
        }

    def _find_counterpart_candidate(self):
        return next(
            (
                cronenberg
                for cronenberg
                in self.universe.cronenbergs
                if getattr(
                    cronenberg,
                    "active",
                    True
                )
                and cronenberg.is_alive
                and cronenberg.quantum_state
                .counterpart_potential
                and not cronenberg.quantum_state
                .counterpart_manifested
                and cronenberg.quantum_state
                .counterpart_id is None
            ),
            None
        )

    @property
    def public_state(self):
        return {
            "name": self.name,
            "resolution_count": len(
                self.history
            )
        }
