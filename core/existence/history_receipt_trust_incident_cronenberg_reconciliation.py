"""Experimental A44 incident-to-Cronenberg reconciliation.

This adapter coordinates a local SQLite incident outbox with
the existing in-memory Universe publication transaction.

For a fresh incident:
1. Record it in the outbox.
2. Publish a Cronenberg and canonical binding event inside
   one Universe rollback transaction.
3. Acknowledge the resulting Cronenberg in the outbox.

For an existing incident:
- Verify the canonical Universe binding before ACK or retry.
- Recover a lost ACK when the live Universe still holds
  the corresponding publication.
- Refuse ambiguous pending or forged delivered records.

The Universe is not independently durable. This module does
not provide cross-process exactly-once guarantees, trusted
storage, malicious rollback protection, or global attack
detection. All rejected operations remain rejected.
"""

from dataclasses import dataclass, field
from threading import RLock
from weakref import WeakKeyDictionary

from core.entity.cronenberg import Cronenberg

from core.existence.history_receipt_trust_attack_cronenberg import (
    SecurityAttackDetected,
)

from core.existence.history_receipt_trust_incident_outbox import (
    SecurityIncidentRecord,
    SecurityIncidentStatus,
    _require_incident_id,
    _require_operation,
)

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)

from universe.cronenberg_publication_transaction import (
    CronenbergPublicationTransaction,
)

from universe.universe import Universe


_LOCK_REGISTRY_GUARD = RLock()
_UNIVERSE_RECONCILIATION_LOCKS = WeakKeyDictionary()


def _lock_for_universe(universe):
    """Return one process-local shared lock per live Universe.

    Registry creation is serialized, so independent
    reconciler objects cannot accidentally use different
    locks for the same Universe.

    Weak keys avoid storing synchronization objects in
    the Universe or retaining discarded Universes.
    """

    with _LOCK_REGISTRY_GUARD:
        lock = _UNIVERSE_RECONCILIATION_LOCKS.get(
            universe
        )

        if lock is None:
            lock = RLock()

            _UNIVERSE_RECONCILIATION_LOCKS[
                universe
            ] = lock

        return lock


_SOURCE = "history_receipt_trust_attack"
_SAFE_ERROR = "A44 blocked security attack."


@dataclass(frozen=True, slots=True)
class SecurityIncidentCronenbergBoundEvent:
    """Canonical in-Universe binding for one security incident."""

    incident_id: str
    cronenberg_id: str
    source_operation: str

    source_component: str = field(
        default=_SOURCE,
        init=False,
    )

    name: str = field(
        default="security_incident_cronenberg_bound",
        init=False,
    )

    type: str = field(
        default="security_incident_manifestation_binding",
        init=False,
    )

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "incident_id": self.incident_id,
            "cronenberg_id": self.cronenberg_id,
            "source_component": self.source_component,
            "source_operation": self.source_operation,
        }


class SecurityIncidentCronenbergReconciler:
    """Fail-closed coordinator for one trusted live Universe.

    An outbox acknowledgement alone is not manifestation
    evidence. Only a consistent canonical Universe binding,
    matching entity and matching manifestation event can
    justify local acknowledgement.

    Concurrent writers and independent processes require
    further coordination. The caller must not treat this
    experimental adapter as a production authorization gate.
    """

    def __init__(self, *, universe, outbox):
        if not isinstance(universe, Universe):
            raise ValueError(
                "A canonical Universe is required."
            )

        for name in ("record", "get", "acknowledge"):
            if not callable(getattr(outbox, name, None)):
                raise ValueError(
                    "A usable security incident outbox is required."
                )

        self._universe = universe
        self._outbox = outbox

    def _find_binding(self, incident_id):
        """Find exactly one canonical incident binding or none."""

        matching = tuple(
            event
            for event in self._universe.quantum_events
            if getattr(event, "incident_id", None)
            == incident_id
        )

        if not matching:
            return None

        if (
            len(matching) != 1
            or type(matching[0])
            is not SecurityIncidentCronenbergBoundEvent
        ):
            raise ValueError(
                "Ambiguous or invalid Universe incident binding."
            )

        return matching[0]

    def _verify_binding(
        self,
        binding,
        *,
        incident_id,
        source_operation,
    ):
        """Verify the live entity and canonical manifestation."""

        if (
            binding.incident_id != incident_id
            or binding.source_operation != source_operation
            or binding.source_component != _SOURCE
        ):
            raise ValueError(
                "Conflicting Universe incident identity."
            )

        matches = tuple(
            entity
            for entity in self._universe.cronenbergs
            if getattr(entity, "id", None)
            == binding.cronenberg_id
        )

        if (
            len(matches) != 1
            or not isinstance(matches[0], Cronenberg)
        ):
            raise ValueError(
                "Bound Cronenberg is missing or ambiguous."
            )

        cronenberg = matches[0]

        if (
            sum(
                entity is cronenberg
                for entity in self._universe.entities
            ) != 1
        ):
            raise ValueError(
                "Bound Cronenberg is not uniquely registered."
            )

        manifests = tuple(
            event
            for event in self._universe.quantum_events
            if (
                isinstance(event, CronenbergManifestedEvent)
                and event.cronenberg_id
                == binding.cronenberg_id
            )
        )

        if len(manifests) != 1:
            raise ValueError(
                "Missing or ambiguous Cronenberg manifestation."
            )

        manifest = manifests[0]

        if (
            manifest.source_component != _SOURCE
            or manifest.source_operation != source_operation
            or manifest.error_type != "RuntimeError"
            or manifest.error_message != _SAFE_ERROR
        ):
            raise ValueError(
                "Cronenberg manifestation provenance mismatch."
            )

        # A Cronenberg cannot be assigned to two incidents.
        for event in self._universe.quantum_events:
            if (
                isinstance(
                    event,
                    SecurityIncidentCronenbergBoundEvent,
                )
                and event.cronenberg_id
                == binding.cronenberg_id
                and event.incident_id != incident_id
            ):
                raise ValueError(
                    "Cronenberg is bound to another incident."
                )

        return cronenberg

    def _acknowledge(
        self,
        *,
        incident_id,
        cronenberg_id,
    ):
        """Persist a local claim only after Universe verification."""

        try:
            result = self._outbox.acknowledge(
                incident_id,
                cronenberg_id,
            )

        except Exception as exc:
            raise ValueError(
                "Security incident rejected; "
                "Cronenberg acknowledgement unavailable."
            ) from exc

        if type(result) is not bool:
            raise ValueError(
                "Invalid incident acknowledgement result."
            )

    @staticmethod
    def _deny(attack):
        raise SecurityAttackDetected(
            "Security attack rejected; "
            "Cronenberg incident reconciled."
        ) from attack

    def _publish(self, *, incident_id, source_operation):
        """Publish manifestation and binding as one Universe unit."""

        def operation():
            # The existing public factory executes its own
            # publication transaction. The OUTER transaction
            # also covers the following binding append.
            cronenberg = (
                self._universe
                .create_cronenberg_from_quantum_error(
                    error=RuntimeError(_SAFE_ERROR),
                    source_component=_SOURCE,
                    source_operation=source_operation,
                )
            )

            if not isinstance(cronenberg, Cronenberg):
                raise ValueError(
                    "Unexpected Cronenberg publication result."
                )

            binding = SecurityIncidentCronenbergBoundEvent(
                incident_id=incident_id,
                cronenberg_id=cronenberg.id,
                source_operation=source_operation,
            )

            self._universe.quantum_events.append(
                binding
            )

            return binding

        try:
            return CronenbergPublicationTransaction.execute(
                self._universe,
                operation,
                participants=(),
            )

        except Exception as exc:
            raise ValueError(
                "Security incident rejected; "
                "Cronenberg publication failed."
            ) from exc

    def reject(
        self,
        *,
        incident_id,
        source_operation,
        attack,
    ):
        """Serialize reconciliation across coordinators of one Universe.

        The lock covers record-before-publish, canonical
        binding lookup, manifestation with rollback,
        acknowledgement and all failure paths.

        It is process-local and does not serialize external
        direct Universe mutations or independent processes.
        """

        with _lock_for_universe(self._universe):
            return self._reject_locked(
                incident_id=incident_id,
                source_operation=source_operation,
                attack=attack,
            )

    def _reject_locked(
        self,
        *,
        incident_id,
        source_operation,
        attack,
    ):
        """Reject a detected attack and reconcile its manifestation.

        A new incident may be published only when the outbox
        confirms the record was newly inserted.

        An existing pending incident without a canonical
        Universe binding is ambiguous and must never cause
        a blind repeat publication.
        """

        if not isinstance(attack, SecurityAttackDetected):
            raise ValueError(
                "Explicit security attack marker required."
            )

        _require_incident_id(incident_id)
        _require_operation(source_operation)

        # Write-ahead incident record. A failure here must
        # prevent any new Universe publication.
        try:
            fresh = self._outbox.record(
                incident_id,
                source_operation,
            )

            record = self._outbox.get(incident_id)

        except Exception as exc:
            raise ValueError(
                "Security incident rejected; "
                "incident storage unavailable or conflicting."
            ) from exc

        if (
            type(fresh) is not bool
            or type(record) is not SecurityIncidentRecord
            or record.incident_id != incident_id
            or record.source_operation != source_operation
        ):
            raise ValueError(
                "Inconsistent security incident record."
            )

        binding = self._find_binding(incident_id)

        if binding is not None:
            cronenberg = self._verify_binding(
                binding,
                incident_id=incident_id,
                source_operation=source_operation,
            )

            if (
                record.status
                is SecurityIncidentStatus.DELIVERED
                and record.cronenberg_id != cronenberg.id
            ):
                raise ValueError(
                    "Incident acknowledgement conflicts "
                    "with canonical Universe publication."
                )

            if record.status is SecurityIncidentStatus.PENDING:
                self._acknowledge(
                    incident_id=incident_id,
                    cronenberg_id=cronenberg.id,
                )

            elif record.status is not SecurityIncidentStatus.DELIVERED:
                raise ValueError(
                    "Unknown incident delivery state."
                )

            self._deny(attack)

        if record.status is SecurityIncidentStatus.DELIVERED:
            raise ValueError(
                "Delivered incident lacks canonical "
                "Universe manifestation evidence."
            )

        if record.status is not SecurityIncidentStatus.PENDING:
            raise ValueError(
                "Unknown incident delivery state."
            )

        if not fresh:
            raise ValueError(
                "Pending incident is ambiguous; "
                "automatic republication denied."
            )

        # This is the first confirmed local registration.
        # A fresh record is not proof that another process
        # has not already published the same incident.
        # Concurrent/cross-process safety is a later phase.
        self._publish(
            incident_id=incident_id,
            source_operation=source_operation,
        )

        binding = self._find_binding(incident_id)

        if binding is None:
            raise ValueError(
                "Published incident has no Universe binding."
            )

        cronenberg = self._verify_binding(
            binding,
            incident_id=incident_id,
            source_operation=source_operation,
        )

        self._acknowledge(
            incident_id=incident_id,
            cronenberg_id=cronenberg.id,
        )

        self._deny(attack)
