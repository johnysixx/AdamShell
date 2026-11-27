"""Atomic authenticated session reservation in protected storage v2.

Session consumption and its complete history commitment are
updated in a single root database transaction.

The caller must hold the canonical backend fence.

Legacy storage is never upgraded implicitly. Legacy sidecar
databases are never imported, recreated or deleted here.

This reference assumes trusted local persistence. The history
digest detects isolated session record modification but cannot
establish resistance to coordinated database modification or
complete trusted storage rollback.
"""

import sqlite3

from dataclasses import dataclass

from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_anchor_enrollment import (
    PinnedProtectedRootAnchorEnrollment,
)

from .history_receipt_trust_checkpoint_protected_provisioning_witness_deployment_floor_writer_policy_protected_root_sqlite_reference import (
    SQLiteProtectedRootBackend,
    _active_leases,
    _require_current_lease,
    storage,
)


_REGISTRY_DOMAIN = (
    "AdamShell/A44/protected-root-anchor-session-registry/v2"
)


@dataclass(frozen=True, slots=True)
class _RegistryBinding:

    descriptor: storage._Storage

    enrollment: PinnedProtectedRootAnchorEnrollment

    def metadata(self):

        return storage._json_bytes([
            _REGISTRY_DOMAIN,
            self.descriptor.storage_id,
            *storage._identity_fields(
                self.descriptor.identity
            ),
            self.enrollment.fingerprint(),
        ])


def _binding(backend, enrollment):

    if type(backend) is not SQLiteProtectedRootBackend:

        raise ValueError(
            "Expected canonical SQLite protected root backend."
        )

    if type(enrollment) is not PinnedProtectedRootAnchorEnrollment:

        raise ValueError(
            "Expected canonical protected anchor enrollment."
        )

    descriptor = backend._storage

    if type(descriptor) is not storage._Storage:

        raise ValueError(
            "Expected canonical protected storage descriptor."
        )

    if descriptor.identity != enrollment.identity:

        raise ValueError(
            "Session registry deployment identity mismatch."
        )

    return _RegistryBinding(
        descriptor=descriptor,
        enrollment=enrollment,
    )


def _require_fence(binding):

    descriptor = binding.descriptor

    lease = _active_leases().get(
        descriptor.fence_path
    )

    if lease is None:

        raise ValueError(
            "Session reservation requires a held backend fence."
        )

    _require_current_lease(
        lease,
        descriptor,
    )


def _reject_legacy_sidecar(binding):

    path = binding.descriptor.path

    sidecar = path.with_name(
        path.name + ".sessions.sqlite3"
    )

    if storage._present(sidecar):

        raise ValueError(
            "Legacy session storage requires explicit migration."
        )


def _require_v2(connection):

    if (
        storage._state_schema_version(connection)
        != storage._STATE_SCHEMA_V2
    ):

        raise ValueError(
            "Authenticated session reservation requires storage v2."
        )


def _validate_binding(connection, binding):

    storage._validate_session_history(
        connection
    )

    rows = connection.execute(
        "SELECT singleton, enrollment, history_digest "
        "FROM session_metadata"
    ).fetchall()

    if len(rows) != 1 or rows[0][0] != 1:

        raise ValueError(
            "Invalid integrated session registry metadata."
        )

    _, enrollment, history_digest = rows[0]

    expected = binding.metadata()

    if enrollment is not None and enrollment != expected:

        raise ValueError(
            "Integrated session registry enrollment mismatch."
        )

    return enrollment, history_digest


def _reserve_in_transaction(
    connection,
    binding,
    session,
):

    if not connection.in_transaction:

        raise ValueError(
            "Session reservation requires an active transaction."
        )

    descriptor = binding.descriptor

    _require_v2(connection)

    current = storage._read_state(
        connection,
        descriptor,
    )

    if current is None:

        raise ValueError(
            "Session registry requires a provisioned root."
        )

    enrollment, previous_digest = _validate_binding(
        connection,
        binding,
    )

    existing = connection.execute(
        "SELECT session FROM consumed_sessions "
        "WHERE session = ?",
        (session,),
    ).fetchone()

    if existing is not None:

        raise ValueError(
            "Protected provider session replay."
        )

    metadata = binding.metadata()

    inserted = connection.execute(
        "INSERT INTO consumed_sessions VALUES (?)",
        (session,),
    )

    if inserted.rowcount != 1:

        raise ValueError(
            "Integrated session insertion failed."
        )

    new_digest = storage._session_history_digest(
        connection
    )

    updated = connection.execute(
        "UPDATE session_metadata "
        "SET enrollment = ?, history_digest = ? "
        "WHERE singleton = 1 "
        "AND enrollment IS ? "
        "AND history_digest = ?",
        (
            metadata,
            new_digest,
            enrollment,
            previous_digest,
        ),
    )

    if updated.rowcount != 1:

        raise ValueError(
            "Integrated session commitment update failed."
        )

    _validate_binding(
        connection,
        binding,
    )

    if connection.execute(
        "SELECT session FROM consumed_sessions "
        "WHERE session = ?",
        (session,),
    ).fetchone() != (session,):

        raise ValueError(
            "Integrated session reservation verification failed."
        )

    if storage._read_state(
        connection,
        descriptor,
    ) != current:

        raise ValueError(
            "Session reservation modified protected root."
        )


def reserve_session(*, backend, enrollment, session):

    """Durably consume one session before signing HOLD."""

    if type(session) is not bytes or len(session) != 32:

        raise ValueError(
            "Canonical 32-byte session required."
        )

    binding = _binding(
        backend,
        enrollment,
    )

    _require_fence(binding)

    try:

        _reject_legacy_sidecar(binding)

        with storage._transaction(
            binding.descriptor.path,
            write=True,
        ) as connection:

            _reserve_in_transaction(
                connection,
                binding,
                session,
            )

            _require_fence(binding)

            _reject_legacy_sidecar(binding)

        # Both the session record and its digest have committed.
        # The independent authorization fence remains held.

        _require_fence(binding)

    except (sqlite3.Error, OSError) as exc:

        raise ValueError(
            "Integrated session reservation failed."
        ) from exc
