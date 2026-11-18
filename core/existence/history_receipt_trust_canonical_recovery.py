"""A44 canonical security publication evidence projection.

This module captures a detached, deterministic projection of
an existing canonical in-memory Universe publication.

Capture requires a live Cronenberg, unique entity registration,
unique manifestation event, and unique incident binding.

parse_untrusted validates structure and SHA-256 consistency.
A checksum does NOT authenticate the producer or prove that
the recorded publication ever existed in a trusted Universe.

verify_live compares evidence against currently registered
canonical objects. It does NOT restore missing objects.

This is not a complete Cronenberg savegame, cross-process
exactly-once mechanism, durable atomic commit, authorization
boundary, or malicious-host tamper/rollback protection.
"""

import hashlib
import json

from dataclasses import dataclass, field

from core.entity.cronenberg import Cronenberg

from core.existence.history_receipt_trust_incident_outbox import (
    _require_cronenberg_id,
    _require_incident_id,
    _require_operation,
)

from core.existence.history_receipt_trust_publication_witness import (
    _require_universe_id,
    _require_digest,
)

from core.existence.history_receipt_trust_incident_cronenberg_reconciliation import (
    SecurityIncidentCronenbergBoundEvent,
    _SOURCE,
    _SAFE_ERROR,
)

from universe.cronenberg_manifestation_state import (
    CronenbergManifestedEvent,
)

from universe.universe import Universe


_SCHEMA_VERSION = 1

_BODY_KEYS = frozenset({
    "schema_version",
    "universe_id",
    "incident_id",
    "source_operation",
    "cronenberg_id",
    "entity",
    "manifestation",
    "binding",
})

_PAYLOAD_KEYS = _BODY_KEYS | {
    "projection_sha256",
}

_ENTITY_KEYS = frozenset({
    "id",
    "type",
})

_MANIFESTATION_KEYS = frozenset({
    "name",
    "type",
    "cronenberg_id",
    "source_component",
    "source_operation",
    "error_type",
    "error_message",
    "quantum_tick",
})

_BINDING_KEYS = frozenset({
    "name",
    "type",
    "incident_id",
    "cronenberg_id",
    "source_component",
    "source_operation",
})


def _exact_mapping(value, expected_keys, subject):
    if (
        type(value) is not dict
        or set(value) != expected_keys
    ):
        raise ValueError(
            f"Invalid canonical publication {subject}."
        )

    return value


def _canonical_json(body):
    """Canonical encoding for this local schema version.

    This encoding deliberately accepts only the exact
    schema-validated primitive projection, not arbitrary
    object serialization.
    """

    try:
        return json.dumps(
            body,
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
            allow_nan=False,
        )

    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(
            "Canonical publication cannot be serialized."
        ) from exc


def _digest_body(body):
    return hashlib.sha256(
        _canonical_json(body).encode("utf-8")
    ).hexdigest()


def _validate_body(body):
    """Validate an exact, self-consistent projection.

    This checks only data format and internal consistency.
    It does not establish that the source is trustworthy.
    """

    _exact_mapping(
        body,
        _BODY_KEYS,
        "projection body",
    )

    if (
        type(body["schema_version"]) is not int
        or body["schema_version"] != _SCHEMA_VERSION
    ):
        raise ValueError(
            "Unsupported canonical publication schema."
        )

    _require_universe_id(
        body["universe_id"]
    )

    _require_incident_id(
        body["incident_id"]
    )

    _require_operation(
        body["source_operation"]
    )

    _require_cronenberg_id(
        body["cronenberg_id"]
    )

    entity = _exact_mapping(
        body["entity"],
        _ENTITY_KEYS,
        "entity",
    )

    if (
        type(entity["id"]) is not str
        or entity["id"] != body["cronenberg_id"]
        or type(entity["type"]) is not str
        or entity["type"] != "cronenberg"
    ):
        raise ValueError(
            "Canonical publication entity identity mismatch."
        )

    manifestation = _exact_mapping(
        body["manifestation"],
        _MANIFESTATION_KEYS,
        "manifestation",
    )

    if (
        type(manifestation["name"]) is not str
        or manifestation["name"] != "cronenberg_manifested"
        or type(manifestation["type"]) is not str
        or manifestation["type"]
        != "quantum_error_manifestation"
        or type(manifestation["cronenberg_id"]) is not str
        or manifestation["cronenberg_id"]
        != body["cronenberg_id"]
        or type(manifestation["source_component"]) is not str
        or manifestation["source_component"] != _SOURCE
        or type(manifestation["source_operation"]) is not str
        or manifestation["source_operation"]
        != body["source_operation"]
        or type(manifestation["error_type"]) is not str
        or manifestation["error_type"] != "RuntimeError"
        or type(manifestation["error_message"]) is not str
        or manifestation["error_message"] != _SAFE_ERROR
        or type(manifestation["quantum_tick"]) is not int
        or manifestation["quantum_tick"] < 0
    ):
        raise ValueError(
            "Canonical publication manifestation mismatch."
        )

    binding = _exact_mapping(
        body["binding"],
        _BINDING_KEYS,
        "binding",
    )

    expected_binding = (
        SecurityIncidentCronenbergBoundEvent(
            incident_id=body["incident_id"],
            cronenberg_id=body["cronenberg_id"],
            source_operation=body["source_operation"],
        ).to_dict()
    )

    if binding != expected_binding:
        raise ValueError(
            "Canonical publication incident binding mismatch."
        )

    # The typed validators above reject bool-as-int,
    # unexpected nested keys and noncanonical values.
    # Return a detached, canonical encoding.
    return _canonical_json(body)


def _capture_live_body(
    *,
    universe,
    incident_id,
    source_operation,
):
    """Inspect a trusted live Universe without changing it."""

    if not isinstance(universe, Universe):
        raise ValueError(
            "A canonical live Universe is required."
        )

    _require_universe_id(universe.id)
    _require_incident_id(incident_id)
    _require_operation(source_operation)

    if not all(
        isinstance(getattr(universe, name, None), list)
        for name in (
            "cronenbergs",
            "entities",
            "quantum_events",
        )
    ):
        raise ValueError(
            "Canonical Universe registries are unavailable."
        )

    # Any event declaring the same incident ID participates
    # in ambiguity detection, even if it is not a canonical
    # SecurityIncidentCronenbergBoundEvent.
    bindings = tuple(
        event
        for event in universe.quantum_events
        if getattr(event, "incident_id", None)
        == incident_id
    )

    if (
        len(bindings) != 1
        or type(bindings[0])
        is not SecurityIncidentCronenbergBoundEvent
    ):
        raise ValueError(
            "Missing or ambiguous canonical incident binding."
        )

    binding = bindings[0]

    if (
        binding.source_component != _SOURCE
        or binding.source_operation != source_operation
        or binding.incident_id != incident_id
    ):
        raise ValueError(
            "Canonical incident binding provenance mismatch."
        )

    _require_cronenberg_id(
        binding.cronenberg_id
    )

    # A live Cronenberg ID must designate exactly one
    # canonical Cronenberg object.
    matching_entities = tuple(
        entity
        for entity in universe.cronenbergs
        if getattr(entity, "id", None)
        == binding.cronenberg_id
    )

    if (
        len(matching_entities) != 1
        or type(matching_entities[0]) is not Cronenberg
    ):
        raise ValueError(
            "Missing or ambiguous canonical Cronenberg."
        )

    entity = matching_entities[0]

    if (
        getattr(entity, "type", None)
        != "cronenberg"
    ):
        raise ValueError(
            "Canonical Cronenberg type mismatch."
        )

    # Reject another registry entry reusing the same ID,
    # not only duplicate references to the same object.
    registered = tuple(
        item
        for item in universe.entities
        if getattr(item, "id", None)
        == entity.id
    )

    if (
        len(registered) != 1
        or registered[0] is not entity
    ):
        raise ValueError(
            "Canonical Cronenberg entity registration mismatch."
        )

    manifestations = tuple(
        event
        for event in universe.quantum_events
        if (
            isinstance(event, CronenbergManifestedEvent)
            and event.cronenberg_id == entity.id
        )
    )

    if (
        len(manifestations) != 1
        or type(manifestations[0])
        is not CronenbergManifestedEvent
    ):
        raise ValueError(
            "Missing or ambiguous canonical manifestation."
        )

    manifestation = manifestations[0]

    if (
        manifestation.source_component != _SOURCE
        or manifestation.source_operation
        != source_operation
        or manifestation.error_type != "RuntimeError"
        or manifestation.error_message != _SAFE_ERROR
        or type(manifestation.quantum_tick) is not int
        or manifestation.quantum_tick < 0
    ):
        raise ValueError(
            "Canonical manifestation provenance mismatch."
        )

    # The same Cronenberg cannot be bound to a second
    # incident. Ambiguous binding is not recoverable.
    for event in universe.quantum_events:
        if (
            type(event)
            is SecurityIncidentCronenbergBoundEvent
            and event.cronenberg_id == entity.id
            and event.incident_id != incident_id
        ):
            raise ValueError(
                "Canonical Cronenberg belongs to another incident."
            )

    body = {
        "schema_version": _SCHEMA_VERSION,
        "universe_id": universe.id,
        "incident_id": incident_id,
        "source_operation": source_operation,
        "cronenberg_id": entity.id,
        "entity": {
            "id": entity.id,
            "type": "cronenberg",
        },
        "manifestation": manifestation.to_dict(),
        "binding": binding.to_dict(),
    }

    _validate_body(body)

    return body


@dataclass(frozen=True, slots=True)
class CanonicalSecurityPublicationEvidence:
    """Immutable detached identity-and-event projection.

    _canonical_body is a string rather than mutable nested
    dictionaries, so callers cannot change the projection
    by editing a returned serialization.

    This is an evidentiary view, not a complete object-state
    snapshot and never a security authority.
    """

    schema_version: int
    universe_id: str
    incident_id: str
    source_operation: str
    cronenberg_id: str

    _canonical_body: str = field(
        repr=False,
    )

    projection_sha256: str

    is_authoritative: bool = field(
        default=False,
        init=False,
    )

    is_restorable: bool = field(
        default=False,
        init=False,
    )

    @classmethod
    def _from_validated_body(cls, body):
        canonical_body = _validate_body(body)

        return cls(
            schema_version=body["schema_version"],
            universe_id=body["universe_id"],
            incident_id=body["incident_id"],
            source_operation=body["source_operation"],
            cronenberg_id=body["cronenberg_id"],
            _canonical_body=canonical_body,
            projection_sha256=hashlib.sha256(
                canonical_body.encode("utf-8")
            ).hexdigest(),
        )

    @classmethod
    def capture(
        cls,
        *,
        universe,
        incident_id,
        source_operation,
    ):
        """Capture a validated, existing live publication."""

        body = _capture_live_body(
            universe=universe,
            incident_id=incident_id,
            source_operation=source_operation,
        )

        return cls._from_validated_body(body)

    @classmethod
    def parse_untrusted(cls, payload):
        """Validate a detached payload without trusting it."""

        _exact_mapping(
            payload,
            _PAYLOAD_KEYS,
            "serialized evidence",
        )

        claimed_digest = _require_digest(
            payload["projection_sha256"]
        )

        body = {
            key: value
            for key, value in payload.items()
            if key != "projection_sha256"
        }

        canonical_body = _validate_body(body)

        expected_digest = hashlib.sha256(
            canonical_body.encode("utf-8")
        ).hexdigest()

        if claimed_digest != expected_digest:
            raise ValueError(
                "Canonical publication projection digest mismatch."
            )

        # Parsing neither authenticates the producer nor
        # authorizes restoration of any Universe object.
        return cls._from_validated_body(body)

    def to_dict(self):
        """Return a fully detached serialization boundary."""

        body = json.loads(
            self._canonical_body
        )

        body["projection_sha256"] = (
            self.projection_sha256
        )

        return body

    def verify_live(self, universe):
        """Compare the projection to an existing live triad.

        No entity, event, registry, outbox, or journal is
        modified. A fresh empty Universe cannot pass.
        """

        # Check the object's own serialized consistency
        # before comparing it with live canonical state.
        self.parse_untrusted(
            self.to_dict()
        )

        if not isinstance(universe, Universe):
            raise ValueError(
                "A canonical live Universe is required."
            )

        if universe.id != self.universe_id:
            raise ValueError(
                "Canonical publication Universe identity mismatch."
            )

        current = type(self).capture(
            universe=universe,
            incident_id=self.incident_id,
            source_operation=self.source_operation,
        )

        if self.to_dict() != current.to_dict():
            raise ValueError(
                "Canonical publication differs from live Universe."
            )

        return True
